from rest_framework import serializers

## models 사용시 필수 / DB파일 사용 시 필요없음.
class MegabusSerializer(serializers.ModelSerializer):
    class Meta:
        pass
