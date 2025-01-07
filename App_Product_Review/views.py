from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Review
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, login, authenticate  # Import logout function
from .forms import RegistrationForm, ProductForm, ReviewForm,PasswordResetForm
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from App_Product_Review.recommender.content_based import get_similar_products_with_explanations
from django.contrib import messages

def is_admin(user):
    return user.is_staff

@login_required
def home_view(request):
    # Fetch latest reviews
    latest_reviews = Review.objects.all().order_by('-created_at')[:10]

    # Get recommended products with explanations
    user = request.user
    recommendations_with_explanations = get_similar_products_with_explanations(user.id)

    # Ensure only products with explanations are included
    filtered_recommendations = [
        (product, explanation)
        for product, explanation in recommendations_with_explanations
        if explanation.strip()  # Include only products with a non-empty explanation
    ]

    return render(request, 'home.html', {
        'latest_reviews': latest_reviews,
        'recommendations_with_explanations': filtered_recommendations,  # Pass filtered recommendations
        'star_range': range(1, 6),
    })

@login_required
def custom_logout_view(request):
    logout(request)
    return redirect('login')

@user_passes_test(is_admin)
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('explore_products')  # Redirect to explore products page
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})

@user_passes_test(is_admin)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return HttpResponseRedirect(reverse('explore_products'))

@user_passes_test(lambda user: user.is_staff)
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return redirect('product_detail', product_id=review.product.id)

@user_passes_test(is_admin)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('explore_products')  # Redirect to the products list page after saving
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/edit_product.html', {'form': form, 'product': product})

@user_passes_test(lambda user: user.is_staff)  # Restrict access to admins
def view_all_user_profiles(request):
    users = User.objects.all()
    user_profiles = []

    for user in users:
        profile = build_user_profile(user.id)  # Use your existing profile builder
        user_profiles.append({
            'username': user.username,
            'email': user.email,
            'profile': profile,
        })

    return render(request, 'registration/view_all_user_profiles.html', {
        'user_profiles': user_profiles,
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()  # Fetch existing reviews for this product

    # Check if the user has already reviewed this product
    user_reviewed = product.reviews.filter(user=request.user).exists()

    if request.method == 'POST' and not user_reviewed:
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Create a new review
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)  # Redirect back to the product detail page
    else:
        form = ReviewForm()

    star_range = range(1, 6)  # This gives you numbers 1 to 5

    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,  # Ensure form is passed to template
        'star_range': star_range,
        'user_reviewed': user_reviewed  # Pass this flag to the template
    })

def custom_register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')  # Redirect to the login page after registration
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def explore_products(request):
    # Get the search query and selected category from the URL parameters
    search_query = request.GET.get('q', '')
    selected_category = request.GET.get('category', '')  # Fetch selected category

    # Filter products based on the search query and category
    products = Product.objects.all()
    if search_query:
        products = products.filter(name__icontains=search_query)
    if selected_category:
        products = products.filter(category=selected_category)

    # Fetch distinct categories for the dropdown
    categories = Product.objects.values_list('category', flat=True).distinct()

    return render(request, 'products/explore_products.html', {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': selected_category,
    })

def reset_password(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            old_password = form.cleaned_data["old_password"]
            new_password = form.cleaned_data["new_password"]

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "No user found with this email.")
                return render(request, "reset_password.html", {"form": form})

            # Check if the old password is correct
            if not user.check_password(old_password):
                messages.error(request, "Old password is incorrect.")
                return render(request, "registration/reset_password.html", {"form": form})

            # Update the password
            user.set_password(new_password)
            user.save()

            messages.success(request, "Password has been reset successfully.")
            return redirect("login")
    else:
        form = PasswordResetForm()

    return render(request, "registration/reset_password.html", {"form": form})

def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def build_user_profile(user):
    reviews = Review.objects.filter(user=user)
    user_profile = []
    for review in reviews:
        product = review.product
        features = f"{product.category} {product.brand} {product.description}"
        user_profile.append(features)
    return " ".join(user_profile)