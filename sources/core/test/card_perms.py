from django.test.testcases import TransactionTestCase
from django.utils import unittest
from django.utils.unittest.suite import TestSuite
from rest_framework.status import HTTP_201_CREATED, HTTP_403_FORBIDDEN, HTTP_200_OK, HTTP_204_NO_CONTENT
from core.models.member import Member
from core.models.role_fields import RoleLevelField
from core.test.auth_tools import auth_api_call, register_api_call
from core.test.card_tools import create_card_api_call, list_cards_api_call, retrieve_card_api_call, delete_card_api_call
from core.test.member_tools import invite_member_api_call, accept_invitation_api_call
from core.test.role_tools import create_role_api_call
from core.test.tools import format_response
from core.test.vault_tools import create_vault_api_call, delete_vault_api_call, list_vaults_api_call, retrieve_vault_api_call
from core.test.workspace_tools import create_workspace_api_call, delete_workspace_api_call, list_workspaces_api_call, retrieve_workspace_api_call
from core.tools.changes import post_change


class ApiCardPermsTest(TransactionTestCase):

    def test_000_vault_anonymous_access(self):
        response = create_vault_api_call(None, name="card_in_workspace", workspace=None)
        self.assertEqual(
            response.status_code,
            HTTP_403_FORBIDDEN,
            format_response(response)
        )

    def test_001_create_delete_vault_as_anonymous(self):

    # create user
        email = 'jan@rclick.cz'
        register_api_call(email=email, nickname='Misan').data
        user1token = auth_api_call(email=email).data.get('token')

        # create workspace
        workspace = create_workspace_api_call(user1token, name='Workspace').data

        #create vault
        vault = create_vault_api_call(user1token, name="vault_in_workspace", workspace=workspace.get('id')).data

        #create card
        card = create_card_api_call(user1token, name="card_in_vault", vault=vault.get('id')).data

        #delete card as anonymous
        response = delete_card_api_call(None, card.get('id'))
        self.assertEqual(
            response.status_code,
            HTTP_403_FORBIDDEN,
            format_response(response)
        )

    def test_010_create_card_in_vault_without_acl_to_vault(self):
        # create user1
        email = 'jan@rclick.cz'
        register_api_call(email=email, nickname='Jan').data
        user1token = auth_api_call(email=email).data.get('token')

        # create user2
        email = 'marcel@rclick.cz'
        register_api_call(email=email, nickname='Marcel').data
        user2token = auth_api_call(email=email).data.get('token')

        # create workspace for user1
        workspace1 = create_workspace_api_call(user1token, name='workspace').data

        # create vault for user1
        vault1 = create_vault_api_call(user1token, name='vault_in_workspace', workspace=workspace1.get('id')).data

        # user2 tries to create vault in workspace of user 2 which he has no access to
        response = create_card_api_call(user2token, name="card_in_vault", vault=vault1.get('id'))
        self.assertEqual(
            response.status_code,
            HTTP_403_FORBIDDEN,
            format_response(response)
        )


    def test_020_create_vault_and_and_check_permissions(self):
        # create user1
        email = 'jan@rclick.cz'
        user1 = register_api_call(email=email, nickname='Jan').data
        user1token = auth_api_call(email=email).data.get('token')

        # create user2
        email = 'marcel@rclick.cz'
        user2 = register_api_call(email=email, nickname='Marcel').data
        user2token = auth_api_call(email=email).data.get('token')

        # create workspace for user1
        workspace1 = create_workspace_api_call(user1token, name='Workspace').data

        # create vault
        vault1 = create_vault_api_call(user1token, name="vault_in_workspace", workspace=workspace1.get('id')).data

        # create card
        card1 = create_card_api_call(user1token, name='card_in_vault', vault=vault1.get('id')).data

        #user1 invites user and grant to user role READ to card1
        user2member = invite_member_api_call(user1token, email=user2.get('email'), workspace=workspace1.get('id')).data
        user2hash = Member.objects.get(pk=user2member.get('id')).invitation_hash
        user2accepted = accept_invitation_api_call(user2token, id=user2member.get('id'), hash=user2hash)
        user2role = create_role_api_call(
            user1token,
            member=user2member.get('id'),
            to_card=card1.get('id'),
            level=RoleLevelField.LEVEL_READ
        )

        #user2 tries to read card, should be allowed
        response = retrieve_card_api_call(user2token, card1.get('id'))
        self.assertEqual(
            response.status_code,
            HTTP_200_OK,
            format_response(response)
        )

        #user2 tries to read vault, should be allowed
        response = retrieve_vault_api_call(user2token, vault1.get('id'))
        self.assertEqual(
            response.status_code,
            HTTP_200_OK,
            format_response(response)
        )

        #user2 tries to read workspace, should be allowed
        response = retrieve_workspace_api_call(user2token, workspace1.get('id'))
        self.assertEqual(
            response.status_code,
            HTTP_200_OK,
            format_response(response)
        )

        #user2 tries to delete card, should be forbidden
        response = delete_card_api_call(user2token, card1.get('id'))
        self.assertEqual(
            response.status_code,
            HTTP_403_FORBIDDEN,
            format_response(response)
        )

        #user2 tries to list workspace of vault1 of card1, should be allowed
        response = list_workspaces_api_call(user2token)
        self.assertEqual(
            len(response.data),
            1,
            format_response(response)
        )

        #user2 tries to delete workspace of vault1, should be forbidden
        response = delete_workspace_api_call(user2token, vault1.get('workspace'))
        self.assertEqual(
            response.status_code,
            HTTP_403_FORBIDDEN,
            format_response(response)
        )

        #user1 grants write to workspace, user2 should be able to delete card
        response = create_role_api_call(
            user1token,
            member=user2member.get('id'),
            to_workspace=workspace1.get('id'),
            level=RoleLevelField.LEVEL_WRITE
        )

        #user2 tries to delete card, should be allowed
        response = delete_card_api_call(user2token, card1.get('id'))
        self.assertEqual(
            response.status_code,
            HTTP_204_NO_CONTENT,
            format_response(response)
        )

    def test_030_retrieve_forbidden(self):
        # create user1
        email = 'jan@rclick.cz'
        register_api_call(email=email, nickname='Jan').data
        user1token = auth_api_call(email=email).data.get('token')

        # create user2
        email = 'marcel@rclick.cz'
        register_api_call(email=email, nickname='Marcel').data
        user2token = auth_api_call(email=email).data.get('token')

        # create workspace for user1
        workspace1 = create_workspace_api_call(user1token, name='workspace').data

        # create vault for user1
        vault1 = create_vault_api_call(user1token, name='vault_in_workspace', workspace=workspace1.get('id')).data

        # create card1
        card1 = create_card_api_call(user1token, name="card_in_vault", vault=vault1.get('id')).data

        # user 2 tries to retrieve card1 should be forbidden
        response = retrieve_card_api_call(user2token, card1.get('id'))
        self.assertEqual(
            response.status_code,
            HTTP_403_FORBIDDEN,
            format_response(response)
        )


def card_perms_suite():
    suite = TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(ApiCardPermsTest))
    return suite