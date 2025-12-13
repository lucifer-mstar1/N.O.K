from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, CoursePart, Enrollment, Review
from .services import purchase_course_part

@login_required
def course_list(request):
    subject = request.GET.get("subject")
    courses = Course.objects.filter(is_active=True)
    if subject:
        courses = courses.filter(subject__icontains=subject)
    return render(request, "courses/course_list.html", {"courses": courses})

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    parts = course.parts.all()
    reviews = course.reviews.select_related("student").order_by("-created_at")[:10]
    avg_rating = course.average_rating()
    return render(request, "courses/course_detail.html", {
        "course": course,
        "parts": parts,
        "reviews": reviews,
        "avg_rating": avg_rating,
    })

@login_required
def buy_part(request, part_id):
    part = get_object_or_404(CoursePart, id=part_id)
    if request.method == "POST":
        try:
            purchase_course_part(request.user, part)
        except ValueError as e:
            messages.error(request, str(e))
        else:
            messages.success(request, f"Purchased {part.name} for {part.price_z} Z. Your XP increased!")
        return redirect("courses:course_detail", pk=part.course.id)
    return redirect("courses:course_detail", pk=part.course.id)

@login_required
def add_review(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        rating = int(request.POST.get("rating", 5))
        comment = request.POST.get("comment", "").strip()
        review, created = Review.objects.update_or_create(
            course=course,
            student=request.user,
            defaults={"rating": rating, "comment": comment},
        )
        messages.success(request, "Thank you for your feedback! Your opinion helps other learners.")
    return redirect("courses:course_detail", pk=course.id)
