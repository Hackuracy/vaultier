from rest_framework.fields import SerializerMethodField, SlugField
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet
from vaultier.api.fields.perms import PermsField
from vaultier.api.member import RelatedMemberSerializer
from vaultier.api.shared.slug import RetrieveBySlugMixin
from vaultier.api.user import RelatedUserSerializer
from vaultier.auth.authentication import TokenAuthentication
from vaultier.models import Workspace
from vaultier.models.acl_fields import AclLevelField
from vaultier.models.member import Member
from vaultier.models.role_fields import RoleLevelField
from vaultier.models.slug import Slug
from vaultier.perms.check import has_object_acl


class CanManageWorkspace(BasePermission):
    def has_object_permission(self, request, view, obj):

        if view.action == 'retrieve' or view.action == 'list' :
            required_level = AclLevelField.LEVEL_READ
        else:
            required_level = AclLevelField.LEVEL_WRITE

        if not obj.pk:
            return True
        else:
            return has_object_acl(request.user, obj, required_level)

class WorkspaceMembershipSerializer(RelatedMemberSerializer):
    class Meta(RelatedMemberSerializer.Meta):
        fields = ('status', 'id', 'workspace_key')


class WorkspaceSerializer(ModelSerializer):
    slug = SlugField(read_only=True)
    created_by = RelatedUserSerializer(required=False)
    perms = PermsField()
    membership = SerializerMethodField('get_membership')

    def get_membership(self, obj):
        member = Member.objects.get_conrete_member_to_workspace(obj, self.user)
        if (member):
            return WorkspaceMembershipSerializer(member).data
        else:
            return None

    class Meta:
        model = Workspace
        fields = ('id', 'slug', 'name', 'description', 'membership', 'perms', 'created_at', 'updated_at', 'created_by')


class RelatedWorkspaceSerializer(WorkspaceSerializer):
    class Meta(WorkspaceSerializer.Meta):
        fields = ['id', 'slug','name']


class WorkspaceViewSet(RetrieveBySlugMixin, ModelViewSet):
    """
    API endpoint that allows workspaces to be viewed or edited.
    """
    model = Workspace
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, CanManageWorkspace)
    serializer_class = WorkspaceSerializer

    def get_serializer(self, *args, **kwargs):
        serializer = super(WorkspaceViewSet, self).get_serializer(*args, **kwargs)
        serializer.user = self.request.user
        return serializer

    def pre_save(self, object):
        if object.pk is None:
            object._user = self.request.user
            object.created_by = self.request.user;
        return super(WorkspaceViewSet, self).pre_save(object)

    def get_queryset(self):
        if self.action == 'list':
            queryset = Workspace.objects.all_for_user(self.request.user)
        else:
            queryset = Workspace.objects.all()
        return queryset