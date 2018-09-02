import functools
from math import ceil
from flask import jsonify
from flask_restful import reqparse


def parse_request(*args, **kwargs):
    """
    Decorator used to parse request arguments.
    This method allows to parse args in different locations then the json body
    (query string, files, form, headers, etc)
    :param args: list of Arguments (flask_restful.reqparse.Argument)
    :return: decorator function
    """
    parser = reqparse.RequestParser(bundle_errors=True)
    for arg in args:
        parser.add_argument(arg)

    if kwargs.get('allow_ordering', None):
        parser_args = [p.name for p in parser.args]
        default_args = [
            reqparse.Argument("sort_by", type=str, store_missing=False),
            reqparse.Argument("order", type=str, store_missing=False, choices=('asc', 'desc')),
        ]
        for p in default_args:
            if p.name not in parser_args:
                parser.add_argument(p)

    def decorator(f):
        @functools.wraps(f)
        def inner(*fargs, **fkwargs):
            fkwargs.update(parser.parse_args())
            return f(*fargs, **fkwargs)

        return inner

    return decorator


def pagination_args_parser(default_page_size=100):
    parser = reqparse.RequestParser()
    parser.add_argument('page', type=int, default=1,
                        help='Page number must be a positive integer.')
    parser.add_argument('count', type=int, default=default_page_size,
                        required=False,
                        help='Items per page must be a positive integer.')
    parser.add_argument('pagination', type=bool, default=True,
                        required=False,
                        help='If "false", return all results in a single page.')
    return parser.parse_args


def paginate_deckbox_results(results, serializer, args_parser=None):
    return get_paginated_response(
        results['cards'],
        serializer,
        results['page'],
        results['count'],
        results['total'],
        results['total_pages']
    )


def paginate_list(results, serializer, args_parser=pagination_args_parser()):
    """Very simple pagination helper for lists.
    This logic could be more elaborated and moved into a class.
    """
    args = args_parser()

    total_items = len(results)

    if not args.pagination:
        return get_paginated_response(results, serializer, 1, total_items, total_items, 1)

    total_pages, page, offset = get_pagination_params(total_items, args.page, args.count)

    return get_paginated_response(
        results[offset:offset + args.count],
        serializer,
        page,
        args.count,
        total_items,
        total_pages
    )


def marshal_with(schema, pagination=False, paginator=paginate_list, args_parser=pagination_args_parser(),
                 success_code=200, **kwargs):
    """Decorator to serialize output using specified schema
    :param kwargs will be passed down to the dump method from marshmallow Schema
    """
    serializer = functools.partial(schema.dump, **kwargs)

    def decorator(f):
        @functools.wraps(f)
        def inner(*fargs, **fkwargs):
            rv = f(*fargs, **fkwargs)
            if pagination:
                if isinstance(rv, list):
                    rv = paginator(rv, serializer, args_parser)
                else:
                    rv = paginator(rv, serializer, args_parser)
            else:
                rv = serializer(rv)
            response = jsonify(rv)
            response.status_code = success_code
            return response

        return inner

    return decorator


def get_pagination_params(total_items, page, count):
    total_pages = int(ceil(total_items / float(count)))
    if page > total_pages:
        page = total_pages

    offset = (page - 1) * count

    if offset < 0:
        offset = 0

    return total_pages, page, offset


def get_paginated_response(items, serializer, page, count, total_items, total_pages):
    return {
        'count': total_items,
        'page': page,
        'items_per_page': count,
        'total_pages': total_pages,
        'items': serializer(items)
    }
