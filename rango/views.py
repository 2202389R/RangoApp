from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Page
from django.template import RequestContext
from rango.models import Category
from django.shortcuts import render_to_response


def encode_url(str):
    return str.replace(' ', '_')

def decode_url(str):
    return str.replace('_', ' ')


def get_category_list(max_results=0, starts_with=''):
	cat_list = []
	if starts_with:
		cat_list = Category.objects.filter(name__startswith=starts_with)
	else:
		cat_list = Category.objects.all()

	if max_results > 0:
		if (len(cat_list) > max_results):
			cat_list = cat_list[:max_results]

	for cat in cat_list:
		cat.url = encode_url(cat.name)

	return cat_list

def index(request):
	context = RequestContext(request)

	top_category_list = Category.objects.order_by('-likes')[:5]
	for category in top_category_list:
		category.url = encode_url(category.name)

	context_dict = {'categories': top_category_list}

	cat_list = get_category_list()
	context_dict['cat_list'] = cat_list

	page_list = Page.objects.order_by('-views')[:5]
	context_dict['pages'] = page_list

	return render_to_response('rango/index.html', context_dict, context)

def about(request):
	context = RequestContext(request)
	context = RequestContext(request)
	context_dict = {}
	cat_list = get_category_list()
	context_dict['cat_list'] = cat_list
	return render_to_response('rango/about.html', context_dict, context)

def show_category(request, category_name_slug):
	# Create a context dictionary which we can pass
	# to the template rendering engine.
	context_dict = {}
	try:
		# Can we find a category name slug with the given name?
		# If we can't, the .get() method raises a DoesNotExist exception.
		# So the .get() method returns one model instance or raises an exception.
		category = Category.objects.get(slug=category_name_slug)
		# Retrieve all of the associated pages.
		# Note that filter() will return a list of page objects or an empty list
		pages = Page.objects.filter(category=category)
		# Adds our results list to the template context under name pages.
		context_dict['pages'] = pages
		# We also add the category object from
		# the database to the context dictionary.
		# We'll use this in the template to verify that the category exists.
		context_dict['category'] = category
	except Category.DoesNotExist:
		# We get here if we didn't find the specified category.
		# Don't do anything -
		# the template will display the "no category" message for us.
		context_dict['category'] = None
		context_dict['pages'] = None
	# Go render the response and return it to the client.
	return render(request, 'rango/category.html', context_dict)


