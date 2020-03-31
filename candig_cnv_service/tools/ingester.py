"""
The ingester module provides methods to ingest entire CNV files
"""

import os
import sys

from sqlalchemy.exc import IntegrityError

sys.path.append(os.getcwd())

from candig_cnv_service.api.exceptions import FileTypeError  # noqa: E402
from candig_cnv_service.api.exceptions import KeyExistenceError  # noqa: E402
from candig_cnv_service.api.exceptions import HeaderError  # noqa: E402
from candig_cnv_service.orm import init_db, get_engine  # noqa: E402
from candig_cnv_service.orm.models import CNV  # noqa: E402


class Ingester:
    def __init__(self, database, patient, sample, cnv_file):
        self.db = "sqlite:///" + database
        self.patient = patient.replace("-", "")
        self.sample = sample
        self.cnv_file = cnv_file
        self.file_type = self.get_type()
        self.engine = self.db_setup()
        self.segments = []
        self.required_headers = [
            'chromosome_number',
            'start_position',
            'end_position',
            'copy_number',
            'copy_number_ploidy_corrected'
            ]
        self.ingests = {
            "csv": self.ingest_csv,
            "tsv": self.ingest_tsv
        }

    def get_type(self):
        if (self.cnv_file.find(".csv") != -1):
            return "csv"
        elif (self.cnv_file.find(".tsv") != -1):
            return "tsv"
        # elif (self.cnv_file.find(".txt") != -1):
        #     return "txt"

        raise FileTypeError(self.cnv_file)

    def db_setup(self):
        init_db(self.db)
        engine = get_engine()
        with engine.connect() as connection:
            result = connection.execute(
                "select * from sample where sample_id=\"{}\""
                .format(self.sample)).first()
            if self.patient != result[1]:
                raise KeyExistenceError(self.sample)
        return engine

    def ingest_tsv(self):

        with open(self.cnv_file) as cnv:
            header = cnv.readline()
            stripped = header.strip("\n").split("\t")
            if not stripped == self.required_headers:
                raise HeaderError(self.required_headers)
            for line in cnv:
                data = line.strip("\n").split("\t")
                segment = dict(zip(self.required_headers, data))
                segment['sample_id'] = self.sample
                self.segments.append(segment)

    def ingest_csv(self):

        with open(self.cnv_file) as cnv:
            header = cnv.readline()
            stripped = header.strip("\n").split(",")
            if not stripped == self.required_headers:
                raise HeaderError(self.required_headers)
            for line in cnv:
                data = line.strip("\n").split(",")
                segment = dict(zip(self.required_headers, data))
                segment['sample_id'] = self.sample
                self.segments.append(segment)

    def upload(self):
        self.ingests[self.file_type]()
        with self.engine.connect() as connection:
            connection.execute(
                CNV.__table__.insert(),
                self.segments
            )

    def upload_sequential(self):
        """
        Should only be called if an integrity error
        in upload() is encountered and --sequential is
        set to true
        """
        with self.engine.connect() as connection:
            for segment in self.segments:
                try:
                    connection.execute(
                        CNV.__table__.insert(),
                        segment
                    )
                except IntegrityError as IE:
                    print(IE.args, IE.params)