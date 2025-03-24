from django.shortcuts import render
from django.core.paginator import Paginator
from django.core.cache import cache
from .scraper import scrape_data               # For Government Services
from .scraper1 import scrape_allgovernmentjobs_selenium, format_state_name  # For Jobs
from .countsraper import scrape_job_count

def job_listings(request):
    # Get active tab. Default to 'jobs'
    tab = request.GET.get('tab', 'jobs')
    
    # Common pagination parameter
    page_no = request.GET.get('page_no', '1')
    try:
        page_no = int(page_no)
        if page_no < 1:
            page_no = 1
    except ValueError:
        page_no = 1

    # Get additional query parameters
    search_query = str(request.GET.get('search', '')).strip()
    category = request.GET.get('category', '').strip()
    filter_type = request.GET.get('filter', 'all')
    
    # Create a unique cache key including page_no
    cache_key = f"job_results_{tab}_{search_query}_{category}_{filter_type}_page{page_no}"
    scraped_data = cache.get(cache_key)
    
    if scraped_data is None:
        scraped_data = []
        scraped_data_1, scraped_data_2 = [], []

        if tab == 'jobs':
            if category:
                # If category is selected, scrape jobs from that category (single page)
                scraped_data_2 = scrape_allgovernmentjobs_selenium(category=category, state_name=None, page_no=page_no, max_pages=1) or []
            elif search_query:
                # Otherwise, use state-based search for jobs
                formatted_state = format_state_name(search_query)
                scraped_data_2 = scrape_allgovernmentjobs_selenium(category=None, state_name=formatted_state, page_no=page_no, max_pages=1) or []
            # Label all job results
            scraped_data = [{**job, 'source': 'All Government Jobs'} for job in scraped_data_2]
        
        elif tab == 'services':
            if search_query:
                scraped_data = scrape_data(search_query, page_no=page_no) or []
            scraped_data = [{**job, 'source': 'Government Services'} for job in scraped_data]
        
        # Cache the scraped data for 1 hour (3600 seconds)
        cache.set(cache_key, scraped_data, timeout=3600)
    
    paginator = Paginator(scraped_data, 20)  # 20 items per page
    page = paginator.get_page(page_no)

    job_count = scrape_job_count()

    context = {
        'scraped_data': page.object_list,
        'tab': tab,
        'search_query': search_query,
        'category': category,
        'filter_type': filter_type,
        'page_no': page_no,
        'paginator': paginator,
        'page': page,
        'job_count': job_count,
    }
    return render(request, 'home.html', context)
