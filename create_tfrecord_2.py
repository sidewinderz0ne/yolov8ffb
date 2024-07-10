import os
import xml.etree.ElementTree as ET
import tensorflow as tf

def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    data = {
        "filename": root.find('filename').text,
        "width": int(root.find('size/width').text),
        "height": int(root.find('size/height').text),
        "objects": []
    }
    
    for obj in root.findall('object'):
        obj_data = {
            "name": obj.find('name').text,
            "xmin": int(obj.find('bndbox/xmin').text),
            "ymin": int(obj.find('bndbox/ymin').text),
            "xmax": int(obj.find('bndbox/xmax').text),
            "ymax": int(obj.find('bndbox/ymax').text)
        }
        data["objects"].append(obj_data)
    
    return data

def create_tf_example(data, image_dir):
    with tf.io.gfile.GFile(os.path.join(image_dir, data['filename']), 'rb') as fid:
        encoded_image = fid.read()
    
    filename = data['filename'].encode('utf8')
    width = data['width']
    height = data['height']
    
    xmins = [obj['xmin'] / width for obj in data['objects']]
    xmaxs = [obj['xmax'] / width for obj in data['objects']]
    ymins = [obj['ymin'] / height for obj in data['objects']]
    ymaxs = [obj['ymax'] / height for obj in data['objects']]
    classes_text = [obj['name'].encode('utf8') for obj in data['objects']]
    classes = [1] * len(data['objects'])  # Assuming all objects belong to the same class

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': tf.train.Feature(int64_list=tf.train.Int64List(value=[height])),
        'image/width': tf.train.Feature(int64_list=tf.train.Int64List(value=[width])),
        'image/filename': tf.train.Feature(bytes_list=tf.train.BytesList(value=[filename])),
        'image/source_id': tf.train.Feature(bytes_list=tf.train.BytesList(value=[filename])),
        'image/encoded': tf.train.Feature(bytes_list=tf.train.BytesList(value=[encoded_image])),
        'image/format': tf.train.Feature(bytes_list=tf.train.BytesList(value=[b'jpg'])),
        'image/object/bbox/xmin': tf.train.Feature(float_list=tf.train.FloatList(value=xmins)),
        'image/object/bbox/xmax': tf.train.Feature(float_list=tf.train.FloatList(value=xmaxs)),
        'image/object/bbox/ymin': tf.train.Feature(float_list=tf.train.FloatList(value=ymins)),
        'image/object/bbox/ymax': tf.train.Feature(float_list=tf.train.FloatList(value=ymaxs)),
        'image/object/class/text': tf.train.Feature(bytes_list=tf.train.BytesList(value=classes_text)),
        'image/object/class/label': tf.train.Feature(int64_list=tf.train.Int64List(value=classes)),
    }))
    return tf_example

def generate_tfrecord(xml_dir, image_dir, output_path):
    writer = tf.io.TFRecordWriter(output_path)
    
    for xml_file in os.listdir(xml_dir):
        if not xml_file.endswith('.xml'):
            continue
        xml_path = os.path.join(xml_dir, xml_file)
        data = parse_xml(xml_path)
        tf_example = create_tf_example(data, image_dir)
        writer.write(tf_example.SerializeToString())
    
    writer.close()
    print(f'Successfully created the TFRecord file: {output_path}')

# Example usage
xml_dir = '/home/grading/yolov8ffb/images/train/all_xml/'
image_dir = '/home/grading/yolov8ffb/images/train/images/'
output_path = '/home/grading/yolov8ffb/images/train/train.tfrecord'

generate_tfrecord(xml_dir, image_dir, output_path)
