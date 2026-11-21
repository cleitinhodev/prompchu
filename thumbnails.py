"""Validate user JPG/PNG and store a small PNG, with no source-path dependency."""
from pathlib import Path
from PySide6.QtCore import QByteArray,QBuffer,QIODevice,QSize,Qt
from PySide6.QtGui import QImageReader

def normalize_image(data):
    if len(data)>20*1024*1024:raise ValueError('A imagem deve ter no máximo 20 MB.')
    buf=QBuffer();buf.setData(QByteArray(data));buf.open(QIODevice.ReadOnly)
    reader=QImageReader(buf);reader.setAutoTransform(True)
    if bytes(reader.format()).lower() not in (b'png',b'jpeg',b'jpg'):raise ValueError('Escolha uma imagem JPG ou PNG válida.')
    size=reader.size()
    if not size.isValid() or size.width()*size.height()>40_000_000:raise ValueError('Imagem inválida ou maior que 40 megapixels.')
    size.scale(QSize(640,400),Qt.KeepAspectRatio);reader.setScaledSize(size)
    img=reader.read()
    if img.isNull():raise ValueError('Não foi possível ler essa imagem.')
    image=QByteArray();out=QBuffer(image);out.open(QIODevice.WriteOnly);img.save(out,'PNG')
    return bytes(image)

def load_thumbnail(path):
    if Path(path).suffix.lower() not in ('.png','.jpg','.jpeg'):raise ValueError('Escolha JPG ou PNG.')
    if Path(path).stat().st_size>20*1024*1024:raise ValueError('A imagem deve ter no máximo 20 MB.')
    return normalize_image(Path(path).read_bytes())
