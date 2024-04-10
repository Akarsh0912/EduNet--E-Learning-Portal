from django.shortcuts import redirect
from django.shortcuts import render
from E_learn.models import Categories, Course, Level, Video, UserCourse, Payment
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib.auth.models import User
from django.contrib import messages
from .settings import *
from django.views.decorators.csrf import csrf_exempt

import razorpay
from time import time


client = razorpay.Client(auth=(KEY_ID, KEY_SECRET))


#  return render(request, 'my_template.html', context)
def base(request):
    return render(request, "base.html")


def home(request):
    category = Categories.objects.all().order_by("id")[0:5]
    course = Course.objects.filter(status="PUBLISH").order_by("id")
    slug = Course.objects.all()

    context = {
        "category": category,
        "course": course,
        "slug": slug,
    }

    return render(request, "Main/home.html", context)


def single_course(request):
    category = Categories.get_all_category(Categories)
    level = Level.objects.all()
    course = Course.objects.all()
    FreeCourse_count = Course.objects.filter(price=0).count()
    PaidCourse_count = Course.objects.filter(price__gte=1).count()

    context = {
        "category": category,
        "level": level,
        "course": course,
        "FreeCourse_count": FreeCourse_count,
        "PaidCourse_count": PaidCourse_count,
    }
    return render(request, "Main/single_course.html", context)


def filter_data(request):
    categories = request.GET.getlist("category[]")
    level = request.GET.getlist("level[]")
    price = request.GET.getlist("price[]")
    print(price)

    if price == ["pricefree"]:
        course = Course.objects.filter(price=0)
    elif price == ["pricepaid"]:
        course = Course.objects.filter(price__gte=1)
    elif price == ["priceall"]:
        course = Course.objects.all()
    elif categories:
        course = Course.objects.filter(category__id__in=categories).order_by("-id")
    elif level:
        course = Course.objects.filter(level__id__in=level).order_by("-id")
    else:
        course = Course.objects.all().order_by("-id")

    t = render_to_string("ajax/course.html", {"course": course})

    return JsonResponse({"data": t})


def contect_us(request):
    category = Categories.get_all_category(Categories)
    context = {
        "category": category,
    }
    return render(request, "Main/contect_us.html", context)


def about_us(request):
    category = Categories.get_all_category(Categories)
    context = {
        "category": category,
    }
    return render(request, "Main/about_us.html", context)


def search_course(request):
    query = request.GET.get("query")
    course = Course.objects.filter(title__icontains=query)
    category = Categories.get_all_category(Categories)
    context = {
        "course": course,
        "category": category,
    }
    return render(request, "search/search.html", context)


def course_details(request, slug):

    if request.user.is_authenticated != True:
        course = Course.objects.filter(slug=slug)
        category = Categories.get_all_category(Categories)
        time_duration = Video.objects.filter(course__slug=slug).aggregate(
            sum=Sum("time_duration")
        )
        course_id = Course.objects.get(slug=slug)

        if course.exists():
            course = course.first()
        else:
            return redirect("404")

        context = {
            "course": course,
            "category": category,
            "time_duration": time_duration,
        }

        return render(request, "course/course_detail.html", context)

    category = Categories.get_all_category(Categories)
    time_duration = Video.objects.filter(course__slug=slug).aggregate(
        sum=Sum("time_duration")
    )

    course_id = Course.objects.get(slug=slug)

    try:
        check_enroll = UserCourse.objects.get(user=request.user, course=course_id)
    except UserCourse.DoesNotExist:
        check_enroll = None

    course = Course.objects.filter(slug=slug)

    if course.exists():
        course = course.first()
    else:
        return redirect("404")

    context = {
        "course": course,
        "category": category,
        "time_duration": time_duration,
        "check_enroll": check_enroll,
    }
    return render(request, "course/course_detail.html", context)


def page_not_found(request):
    category = Categories.get_all_category(Categories)
    context = {
        "category": category,
    }
    return render(request, "error/404.html", context)


def checkOut(request, slug):
    course = Course.objects.get(slug=slug)
    action = request.GET.get("action")
    order = None
    if course.price == 0:
        course = UserCourse(user=request.user, course=course)
        course.save()
        messages.success(request, "COURSE IS SUCCESSGULLY ENROLLED")
        return redirect("my_course")

    elif action == "create_payment":
        if request.method == "POST":
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            country = request.POST.get("country")
            address_1 = request.POST.get("address_1")
            address_2 = request.POST.get("address_2")
            city = request.POST.get("city")
            state = request.POST.get("state")
            postcode = request.POST.get("postcode")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            order_comments = request.POST.get("order_comments")

            amount_cal = course.price - (course.price * course.discount / 100)
            amount = int(amount_cal) * 100
            currency = "INR"
            notes = {
                "name": f"{first_name} {last_name}",
                "country": country,
                "address": f"{address_1} {address_2}",
                "city": city,
                "state": state,
                "postcode": postcode,
                "phone": phone,
                "email": email,
                "order_comments": order_comments,
            }

            receipt = f"SKola-{int(time())}"
            order = client.order.create(
                {
                    "receipt": receipt,
                    "notes": notes,
                    "amount": amount,
                    "currency": currency,
                }
            )

            payment = Payment(
                course=course, user=request.user, order_id=order.get("id")
            )
            payment.save()

    context = {
        "course": course,
        "order": order,
    }

    return render(request, "checkout/checkout.html", context)


def my_course(request):
    if request.user.is_authenticated:
        course = UserCourse.objects.filter(user=request.user)
    else:
        return render(request, "registration/login.html")
    context = {
        "course": course,
    }

    return render(request, "course/mycourse.html", context)


@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = request.POST
        try:
            client.utility.verify_payment_signature(data)
            rezorpay_order_id = data.get("razorpay_order_id")
            razorpay_payment_id = data.get("razorpay_order_id")

            payment = Payment.objects.get(order_id=rezorpay_order_id)
            payment.payment_id = razorpay_payment_id
            payment.status = True

            usercourse = UserCourse(
                user=payment.user,
                course=payment.course,
            )

            usercourse.save()

            payment.user_course = usercourse
            payment.save()

            context = {
                "data": data,
                "payment": payment,
            }
            return render(request, "verify_payment/success.html", context)
        except:
            return render(request, "verify_payment/fail.html")


def watch_course(request, slug):
    lecture = request.GET.get("lecture")
    course_id = Course.objects.get(slug=slug)
    course = Course.objects.filter(slug=slug)
    try:
        check_enroll = UserCourse.objects.get(user=request.user, course=course_id)
        video = Video.objects.filter(youtube_id=lecture).first()

        if course.exists():
            course = course.first()
        else:
            return redirect("404")
    except UserCourse.DoesNotExist:
        return redirect("404")

    context = {"course": course, "video": video, "lecture": lecture}
    return render(request, "course/watch_course.html", context)


def subscribe(request):
    if request.user.is_authenticated:
        return render(request, "subscribe/subscribe.html")
    else:
        return render(request, "registration/login.html")
