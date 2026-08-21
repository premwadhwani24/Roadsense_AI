import glob
import os
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse

import supervisely as sly
from dataset_tools.convert import unpack_if_archive
from supervisely.io.fs import file_exists, get_file_name, get_file_name_with_ext
from tqdm import tqdm

import src.settings as s


def download_dataset(teamfiles_dir: str) -> str:
    """Use it for large datasets to convert them on the instance"""
    api = sly.Api.from_env()
    team_id = sly.env.team_id()
    storage_dir = sly.app.get_data_dir()

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, str):
        parsed_url = urlparse(s.DOWNLOAD_ORIGINAL_URL)
        file_name_with_ext = os.path.basename(parsed_url.path)
        file_name_with_ext = unquote(file_name_with_ext)

        sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
        local_path = os.path.join(storage_dir, file_name_with_ext)
        teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

        fsize = api.file.get_directory_size(team_id, teamfiles_dir)
        with tqdm(
            desc=f"Downloading '{file_name_with_ext}' to buffer...",
            total=fsize,
            unit="B",
            unit_scale=True,
        ) as pbar:
            api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)
        dataset_path = unpack_if_archive(local_path)

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, dict):
        for file_name_with_ext, url in s.DOWNLOAD_ORIGINAL_URL.items():
            local_path = os.path.join(storage_dir, file_name_with_ext)
            teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

            if not os.path.exists(get_file_name(local_path)):
                fsize = api.file.get_directory_size(team_id, teamfiles_dir)
                with tqdm(
                    desc=f"Downloading '{file_name_with_ext}' to buffer...",
                    total=fsize,
                    unit="B",
                    unit_scale=True,
                ) as pbar:
                    api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)

                sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
                unpack_if_archive(local_path)
            else:
                sly.logger.info(
                    f"Archive '{file_name_with_ext}' was already unpacked to '{os.path.join(storage_dir, get_file_name(file_name_with_ext))}'. Skipping..."
                )

        dataset_path = storage_dir
    return dataset_path


def count_files(path, extension):
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                count += 1
    return count


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    ### Function should read local dataset and upload it to Supervisely project, then return project info.###
    dataset_path = "/home/alex/DATASETS/TODO/RoadDamageDetector/RDD2022_all_countries"
    batch_size = 30

    def create_ann(image_path):
        labels = []
        tags = []

        folder = image_path.split("/")[-4]
        tag_meta = folder_to_meta.get(folder)
        tag_country = sly.Tag(tag_meta)
        tags.append(tag_country)
        if folder in ["China_Drone", "China_MotorBike"]:
            view_value = folder.split("_")[1]
            view_meta = folder_to_meta.get(view_value)
            view = sly.Tag(view_meta)
            tags.append(view)

        ann_path = image_path.replace("images", "annotations/xmls").replace(".jpg", ".xml")
        if file_exists(ann_path):
            tree = ET.parse(ann_path)
            root = tree.getroot()
            img_wight = int(root.find(".//width").text)
            img_height = int(root.find(".//height").text)
            objects_content = root.findall(".//object")
            for obj_data in objects_content:
                label_tags = []
                name = obj_data.find(".//name").text
                obj_class = index_to_class.get(name)
                if obj_class is not None:
                    detail_value = index_to_value.get(name)
                    if detail_value is not None:
                        detail = sly.Tag(detail_meta, value=detail_value)
                        label_tags.append(detail)
                    bndbox = obj_data.find(".//bndbox")
                    top = float(bndbox.find(".//ymin").text)
                    left = float(bndbox.find(".//xmin").text)
                    bottom = float(bndbox.find(".//ymax").text)
                    right = float(bndbox.find(".//xmax").text)

                    rectangle = sly.Rectangle(top=top, left=left, bottom=bottom, right=right)
                    label = sly.Label(rectangle, obj_class, tags=label_tags)
                    labels.append(label)

            return sly.Annotation(img_size=(img_height, img_wight), labels=labels, img_tags=tags)

    longitudinal = sly.ObjClass("longitudinal crack", sly.Rectangle)
    transverse = sly.ObjClass("transverse crack", sly.Rectangle)
    alligator = sly.ObjClass("alligator crack", sly.Rectangle)
    pothole = sly.ObjClass("pothole", sly.Rectangle)
    other = sly.ObjClass("other corruption", sly.Rectangle)
    # block = sly.ObjClass("block crack", sly.Rectangle)
    # repair = sly.ObjClass("repair", sly.Rectangle)

    index_to_class = {
        "D00": longitudinal,
        "D01": longitudinal,
        "D0w0": longitudinal,
        "D10": transverse,
        "D11": transverse,
        "D20": alligator,
        "D40": pothole,
        "D43": other,
        "D44": other,
    }

    drone_meta = sly.TagMeta("China_Drone", sly.TagValueType.NONE)
    motorbike_meta = sly.TagMeta("China_Motorbike", sly.TagValueType.NONE)
    czech_meta = sly.TagMeta("Czech", sly.TagValueType.NONE)
    india_meta = sly.TagMeta("India", sly.TagValueType.NONE)
    japan_meta = sly.TagMeta("Japan", sly.TagValueType.NONE)
    norway_meta = sly.TagMeta("Norway", sly.TagValueType.NONE)
    us_meta = sly.TagMeta("United States", sly.TagValueType.NONE)
    detail_meta = sly.TagMeta("detail", sly.TagValueType.ANY_STRING)

    folder_to_meta = {
        "China_Drone": drone_meta,
        "China_MotorBike": motorbike_meta,
        "Czech": czech_meta,
        "India": india_meta,
        "Japan": japan_meta,
        "Norway": norway_meta,
        "United_States": us_meta,
    }

    index_to_value = {
        "D00": "wheel mark part",
        "D01": "construction joint part",
        "D10": "equal interval",
        "D11": "construction joint part",
        "D20": "partial pavement, overall pavement",
        "D40": "rutting, bump, pothole, separation",
        "D43": "crosswalk blur",
        "D44": "white line blur",
    }

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    meta = sly.ProjectMeta(
        obj_classes=[longitudinal, transverse, alligator, pothole, other],
        tag_metas=[
            drone_meta,
            motorbike_meta,
            czech_meta,
            india_meta,
            japan_meta,
            norway_meta,
            us_meta,
            detail_meta,
        ],
    )
    api.project.update_meta(project.id, meta.to_json())

    train_images_pathes = glob.glob(dataset_path + "/*/train/images/*.jpg")
    test_images_pathes = glob.glob(dataset_path + "/*/test/images/*.jpg")

    ds_name_to_data = {"train": train_images_pathes, "test": test_images_pathes}

    for ds_name, images_pathes in ds_name_to_data.items():
        dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

        progress = sly.Progress("Create dataset {}".format(ds_name), len(images_pathes))

        for img_pathes_batch in sly.batched(images_pathes, batch_size=batch_size):
            images_names_batch = [
                get_file_name_with_ext(image_path) for image_path in img_pathes_batch
            ]

            img_infos = api.image.upload_paths(dataset.id, images_names_batch, img_pathes_batch)
            img_ids = [im_info.id for im_info in img_infos]

            if ds_name == "train":
                anns_batch = [create_ann(image_path) for image_path in img_pathes_batch]
                api.annotation.upload_anns(img_ids, anns_batch)

            progress.iters_done_report(len(images_names_batch))

    return project
