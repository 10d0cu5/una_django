import glob
import os

import pandas as pd
from datetime import datetime
from django.conf import settings
from django.core.management import BaseCommand
from loguru import logger

from una_app.models import User, LogEntry


class Command(BaseCommand):
    help = 'Writes data from /sample-data to the database'

    def handle(self, *args, **options):
        csv_samples = glob.glob(os.path.join(settings.DEMO_DATA_DIR, "*.csv"))
        for csv in csv_samples:
            file = open(csv)
            user_id = file.readline().split(',')[-1].rstrip()

            if not User.objects.filter(pk=user_id).exists():
                new_user = User(user_id=user_id)
                new_user.save()
            else:
                logger.info(f"User {user_id} already created")

            df = pd.read_csv(csv, header=1)



            for index, entry in df.iterrows():
                try:
                    new_log_entry = LogEntry(device=entry.get('Gerät',None),
                                         device_serial_number=entry.get('Seriennummer',None),
                                         device_timestamp=datetime.strptime(entry.get('Gerätezeitstempel',None), "%d-%m-%Y %H:%M"),
                                         device_record_type=entry.get('Aufzeichnungstyp',None),
                                         glucose_value=entry.get('Glukosewert-Verlauf mg/dL',None),
                                         user=User.objects.get(pk=user_id)
                                         )
                    new_log_entry.save()
                except Exception as e:
                    logger.info(f"Error on writing{entry} with {e}")

