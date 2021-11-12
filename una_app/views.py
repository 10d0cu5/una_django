# Create your views here.
import csv
from datetime import datetime

import pandas as pd
from django.core.management import call_command
from django.core.paginator import Paginator
from django.db.models import Q
from itertools import chain
from loguru import logger
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from una_app.models import LogEntry, LogEntrySerializer


def user_id_required():
    def decorator(view_func):
        def wrap(request, *args, **kwargs):
            user_id = request.headers.get('user-id', None)
            if user_id:
                return view_func(request, user_id=user_id, *args, **kwargs)
            else:
                return Response({'status': 'failure', 'message': 'no user_id specified'},
                                status=status.HTTP_401_UNAUTHORIZED)

        return wrap

    return decorator


def __get_filtered_logs(user_id: str,
                        start: datetime = None,
                        stop: datetime = None,
                        page: int = None,
                        size: int = None,
                        high: int = None,
                        low: int = None,
                        order: str = None):
    if order and order == "ASC":
        order = "-device_timestamp"
    else:
        order = "device_timestamp"
    if user_id:
        queryset = LogEntry.objects.filter(user__pk=user_id).order_by(order)
    else:
        queryset = LogEntry.objects.all()

    if (start and stop) and start > stop:
        queryset = queryset.filter(device_timestamp__range=
                                   [start, stop])

    if high and low:
        queryset = queryset.filter(glucose_value__lte=int(low)) | queryset.filter(glucose_value__gte=int(high))
    elif high and not low:
        queryset = queryset.filter(glucose_value__gte=high)
    elif low and not high:
        queryset = queryset.filter(glucose_value__lte=low)

    if page and size:
        paginator = Paginator(queryset, size)
        queryset = paginator.page(int(page)+1)
    return queryset


def __convert_date(date_str: str):
    return datetime.strptime(date_str, "%d-%m-%Y %H:%M")


@api_view(['GET'])
@parser_classes([JSONParser])
@user_id_required()
def export_glucose_levels(request, user_id: str, format: str = "json") -> Response:
    start: str = request.GET.get('start', None)
    stop: str = request.GET.get('stop', None)
    page: int = request.GET.get('page', None)
    size: int = request.GET.get('size', None)
    order: str = request.GET.get('order', None)

    if start:
        start_time = __convert_date(start)
    else:
        start_time = None
    if stop:
        end_time = __convert_date(stop)
    else:
        end_time = None

    try:
        qs = __get_filtered_logs(user_id=user_id, start=start_time, stop=end_time, page=page, size=size, order=order)
    except Exception as e:
        logger.error(f"Error on filtering the queryset with error {e}")
        return Response({'status': 'failure', 'message': 'Error on filtering Dataset'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    serialized = LogEntrySerializer(qs, many=True).data
    if format == "json":
        return Response(serialized, status=status.HTTP_200_OK)
    elif format == "csv":
        df = pd.read_json(serialized)
        response = Response(content_type='text/csv', status=status.HTTP_200_OK)
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        writer = csv.writer(response, delimiter=',')  # I always like to specify the delimeter
        writer.writerow(df.columns)
        for index, row in df.iterrows():
            writer.writerow([
                row[df.colums[0]],
                row[df.colums[1]],
                row[df.colums[2]],
                row[df.colums[3]],
                row[df.colums[4]],
                row[df.colums[5]],
                row[df.colums[6]],
            ])

        return response
    else:
        return Response({'status': 'failure', 'message': 'unknown export format'},
                        status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@parser_classes([JSONParser])
@user_id_required()
def get_glucose_highlow(request, user_id: str) -> Response:
    start: str = request.GET.get('start', None)
    stop: str = request.GET.get('stop', None)
    high: int = request.GET.get('high', None)
    low: int = request.GET.get('low', None)
    page: int = request.GET.get('page', None)
    size: int = request.GET.get('size', None)

    if start:
        start_time = __convert_date(start)
    else:
        start_time = None
    if stop:
        end_time = __convert_date(stop)
    else:
        end_time = None

    if not high and not low:
        return Response({'status': 'failure', 'message': 'no upper and/or lower glucose bounds'},
                        status=status.HTTP_404_NOT_FOUND)
    try:
        qs = __get_filtered_logs(page=page, size=size,user_id=user_id, start=start_time, stop=end_time, high=high, low=low)
    except Exception as e:
        logger.error(f"Error on filtering the queryset with error {e}")
        return Response({'status': 'failure', 'message': 'Error on filtering Dataset'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'status': 'success', 'data': LogEntrySerializer(qs, many=True).data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@parser_classes([JSONParser])
@user_id_required()
def get_glucose_levels(request, user_id: str, entry_id: int = None) -> Response:
    start: str = request.GET.get('start', None)
    stop: str = request.GET.get('stop', None)
    page: int = request.GET.get('page', None)
    size: int = request.GET.get('size', None)
    order: str = request.GET.get('order', None)
    if entry_id:
        entry = LogEntry.objects.filter(pk=entry_id)
        logger.info(entry[0])
        if entry:
            return Response({'status': 'success', 'data': LogEntrySerializer(entry, many=True).data},
                            status=status.HTTP_200_OK)
        else:
            return Response({'status': 'failure', 'message': f'no entry matching id {entry_id} found'},
                            status=status.HTTP_404_NOT_FOUND)

    if start:
        start_time = __convert_date(start)
    else:
        start_time = None
    if stop:
        end_time = __convert_date(stop)
    else:
        end_time = None

    qs = __get_filtered_logs(user_id=user_id,
                             start=start_time,
                             stop=end_time,
                             page=page,
                             size=size,
                             order=order)

    return Response({'status': 'success', 'data': LogEntrySerializer(qs, many=True).data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@parser_classes([JSONParser])
def populate_dataset(request) -> Response:
    try:
        call_command('write_test_data')
        logger.info(LogEntry.objects.all())
    except Exception as e:
        return Response({'status': 'error', 'message': f"Error on populating data {e}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'status': 'success'})
