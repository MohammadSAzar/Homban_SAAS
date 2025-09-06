from django import template

register = template.Library()


@register.inclusion_tag('dashboard/pagination.html')
def pagination(page_obj, request, url_name='rent_file_list'):
    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages

    # Build query string without page parameter
    query_params = []
    for key, value in request.GET.items():
        if key != 'page':
            query_params.append(f"{key}={value}")
    query_string = '&'.join(query_params)
    if query_string:
        query_string = '&' + query_string

    # Determine which pages to show
    if total_pages <= 4:
        # Show all pages if 4 or fewer
        pages_to_show = list(range(1, total_pages + 1))
        show_dots_before = False
        show_dots_after = False
        show_first = False
        show_last = False
    else:
        # Always try to show 3 pages: previous, current, next
        start_page = max(1, current_page - 1)
        end_page = min(total_pages, current_page + 1)

        # Adjust to always show 3 pages when possible
        if end_page - start_page < 2:
            if start_page == 1:
                end_page = min(3, total_pages)
            elif end_page == total_pages:
                start_page = max(1, total_pages - 2)

        pages_to_show = list(range(start_page, end_page + 1))

        # Determine if we need to show first page and dots before
        show_first = start_page > 1
        show_dots_before = start_page > 2

        # Determine if we need to show last page and dots after  
        show_last = end_page < total_pages
        show_dots_after = end_page < total_pages - 1

    return {
        'page_obj': page_obj,
        'pages_to_show': pages_to_show,
        'show_dots_before': show_dots_before,
        'show_dots_after': show_dots_after,
        'show_first': show_first,
        'show_last': show_last,
        'first_page': 1,
        'last_page': total_pages,
        'query_string': query_string,
        'url_name': url_name,
    }


