import pickle

from google.cloud import storage
from tempfile import NamedTemporaryFile

def upload_blob(project_id, bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)


def load_blob(project_id, bucket_name, destination_path, filename):
    storage_client = storage.Client(project=project_id)

    with NamedTemporaryFile(mode='rb') as tempfile:
        gcs_path = os.path.join(destination_path, '{filename}'.format(filename=filename))
        storage_client.bucket(bucket_name).blob(gcs_path).download_to_filename(tempfile.name)
        tempfile.seek(0)
        return pickle.load(tempfile)
