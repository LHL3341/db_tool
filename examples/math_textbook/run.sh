cd /mnt/dhwfile/raise/user/linhonglin/data_process/db_tool

export AWS_ACCESS_KEY_ID=FB7QKWTWP279SQMLBX4H
export AWS_SECRET_ACCESS_KEY=dN6ph2f9cQcVhnOCngiGKwPUjMqpM9o4oiKM67mb
export DATA_NAME=math_textbook
python -m main --config examples/${DATA_NAME}/config.yaml

python split_md_for_extract.py --root_dir outputs/${DATA_NAME} --processed_dir processed/${DATA_NAME}

python download_images.py --dir processed/math_textbook