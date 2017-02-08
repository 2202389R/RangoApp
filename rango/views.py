from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Page
from django.template import RequestContext
from rango.models import Category
from django.shortcuts import render_to_response
from rango.forms import CategoryForm, PageForm

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

def add_category(request):
	form = CategoryForm()
	# A HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		# Have we been provided with a valid form?
		if form.is_valid():
			# Save the new category to the database.
			form.save(commit=True)
			# Now that the category is saved
			# We could give a confirmation message
			# But since the most recent category added is on the index page
			# Then we can direct the user back to the index page.
			return index(request)
		else:
			# The supplied form contained errors -
			# just print them to the terminal.
			print(form.errors)
	# Will handle the bad form, new form, or no form supplied cases.
	# Render the form with error messages (if any).
	return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
	context = RequestContext(request)
	context_dict = {}
	category_name = decode_url(category_name_slug)
	try:
		category = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		category = None
	form = PageForm(request.POST)
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()
				return show_category(request, category_name_slug)
		else:
			print(form.errors)
	context_dict['category_name_slug'] = category_name_slug
	context_dict['category_name'] = category_name
	context_dict['form'] = form
	return render(request, 'rango/add_page.html', context_dict,context)


