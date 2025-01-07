from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from App_Product_Review.models import Product, Review
import pandas as pd
def get_similar_products_with_explanations(user_id):

    user_profile_text = build_user_profile(user_id)

    if not user_profile_text:
        return []  # If no reviews, return an empty list

    # Get all product descriptions
    products = Product.objects.all()
    product_descriptions = []

    for product in products:
        product_description = f"{product.category} {product.brand} {product.description}"
        product_descriptions.append(product_description)

    # Append the user profile as the last item in the list of descriptions
    descriptions = product_descriptions + [user_profile_text]

    # Use TF-IDF Vectorizer to convert the text into vectors
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(descriptions)
    save_tfidf_matrix_to_csv(tfidf, tfidf_matrix, descriptions)

    # Compute cosine similarity between the user profile (last row) and all products (all rows except the last one)
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])

    # Get the indices of the most similar products
    similar_indices = cosine_sim.argsort()[0, -6:-1]  # Top 5 similar products

    # Extract feature contributions for explanation
    feature_names = tfidf.get_feature_names_out()
    user_profile_vector = tfidf_matrix[-1].toarray()[0]
    recommendations = []

    for idx in similar_indices:
        product_vector = tfidf_matrix[idx].toarray()[0]
        product_features = []

        for i, value in enumerate(product_vector):
            if value > 0 and user_profile_vector[i] > 0:
                product_features.append((feature_names[i], user_profile_vector[i] * value))

        # Sort features by contribution to similarity
        product_features.sort(key=lambda x: x[1], reverse=True)

        # Format explanation as a string
        explanation = ", ".join([f"{feature} (score: {score:.2f})" for feature, score in product_features[:5]])

        # Convert idx to Python int before using it
        recommendations.append((products[int(idx)], explanation))

    return recommendations

def build_user_profile(user_id):
    """
    Build a user profile based on the products they have reviewed.
    """
    reviews = Review.objects.filter(user_id=user_id)#retrieve all users
    user_profile = []#blank user profile

    for review in reviews:
        product = review.product
        features = f"{product.category} {product.brand} {product.description}"
        user_profile.append(features)
        #create user profile based on category, brand and description and return it as a string

    return " ".join(user_profile)

def save_tfidf_matrix_to_csv(tfidf, tfidf_matrix, descriptions):
    """
    Save the TF-IDF matrix to a CSV file for inspection.
    """
    # Get feature names (unique words) from the vectorizer
    feature_names = tfidf.get_feature_names_out()

    # Convert the sparse matrix to a dense array
    dense_matrix = tfidf_matrix.toarray()

    # Create a DataFrame for better visualization
    df = pd.DataFrame(dense_matrix, columns=feature_names, index=[f"Product {i+1}" for i in range(len(descriptions) - 1)] + ["User Profile"])

    # Save the DataFrame to a CSV file
    df.to_csv("tfidf_matrix.csv", index=True)

    print("TF-IDF matrix saved to tfidf_matrix.csv")