from whitenoise.storage import CompressedManifestStaticFilesStorage

class CustomWhiteNoiseStorage(CompressedManifestStaticFilesStorage):
    # Esta é a variável mágica. 
    # Ao colocar aqui na classe, o Django aceita sem reclamar e o 
    # WhiteNoise passa a ignorar as imagens em falta do CKEditor!
    manifest_strict = False