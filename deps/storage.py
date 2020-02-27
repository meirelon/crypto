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
        gcs_path = os.path.join(destination_path, f'{filename}')
        storage_client.bucket(bucket_name).blob(gcs_path).download_to_filename(tempfile.name)
        tempfile.seek(0)
        return pickle.load(tempfile)


def get_buy_history(project, bucket, ticker, passphrase):
    try:
        # Read in buy history from storage
        buy_history = load_blob(project_id=project,
                                bucket_name=bucket,
                                destination_path=ticker.lower(),
                                filename=f"{passphrase}_buy_history.pkl")
    except:
        # if the buy history for this account does not exist
        # create a new list and upload to storage
        buy_history = []
        pickle.dump(buy_history, open("/tmp/buy_history.pkl", "wb"))
        upload_blob(project_id=project,
                        bucket_name=bucket,
                        source_file_name="/tmp/buy_history.pkl",
                        destination_blob_name=f"{ticker.lower()}/{passphrase}_buy_history.pkl")
    return buy_history


def dump_and_upload(obj, project_id, bucket_name, ticker, passphrase):
    # temp storage for lambda
    pickle.dump(obj, open(f"/tmp/{obj.lower()}.pkl", "wb"))

    # util function to upload buy history to storage
    upload_blob(project_id=project,
                    bucket_name=bucket,
                    source_file_name=f"/tmp/{obj.lower()}.pkl",
                    destination_blob_name=f"{ticker.lower()}/{passphrase}_buy_history.pkl")
