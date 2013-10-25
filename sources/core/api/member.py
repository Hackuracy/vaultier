from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from core.api.user import CreatedByUserSerializer
from core.api.workspace import WorkspaceSerializer
from core.auth import TokenAuthentication
from core.models.member import Member

class MemberSerializer(ModelSerializer):
    created_by = CreatedByUserSerializer(required=False)
    email = SerializerMethodField('get_email')
    nickname = SerializerMethodField('get_nickname')
    user = CreatedByUserSerializer(required=False)
    workspace = WorkspaceSerializer()

    def get_email(self, obj):
        if (obj.status == 'i'):
            return obj.invitation_email
        else:
            return obj.user.email

    def get_nickname(self, obj):
        if (obj.status == 'i'):
            return obj.invitation_email
        else:
            return obj.user.nickname

    class Meta:
        model = Member
        fields = ('status', 'email', 'nickname', 'workspace', 'user', 'created_by', 'created_at', 'updated_at')

class MemberViewSet(ModelViewSet):
    model = Member
    serializer_class = MemberSerializer
    # authentication_classes = (TokenAuthentication,)

    def pre_save(self, object):
        if object.pk is None:
            object.created_by = self.request.user;
        return super(MemberViewSet, self).pre_save(object)

    def get_queryset(self):
        queryset = Member.objects.all()
        return queryset
