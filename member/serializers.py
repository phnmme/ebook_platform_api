from rest_framework import serializers
from .models import SystemUser, UsageHistory

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemUser
        fields = ['fullname', 'username', 'email', 'password', 'phone', 'role', 'idcard', 'expertise']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        role = attrs.get('role')
        idcard = attrs.get('idcard')
        expertise = attrs.get('expertise')

        if role == 'author':
            if not idcard:
                raise serializers.ValidationError({"idcard": "Author ต้องอัปโหลด ID Card"})
            if not expertise:
                raise serializers.ValidationError({"expertise": "Author ต้องกรอก expertise"})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = SystemUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
    


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemUser
        exclude = ['password']


class UsageHistorySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.userid", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UsageHistory
        fields = ["user_id", "user_email", "action", "timestamp"]
