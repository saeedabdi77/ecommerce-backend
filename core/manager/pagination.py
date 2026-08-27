def get_page_window(page_obj, *, window=2, max_without_window=7):
    paginator = page_obj.paginator
    total = paginator.num_pages
    current = page_obj.number

    if total <= max_without_window:
        return list(range(1, total + 1))

    pages = {1, total}

    for page in range(max(1, current - window), min(total, current + window) + 1):
        pages.add(page)

    sorted_pages = sorted(pages)
    window_pages = []
    previous = None

    for page in sorted_pages:
        if previous is not None and page - previous > 1:
            window_pages.append(None)
        window_pages.append(page)
        previous = page

    return window_pages
