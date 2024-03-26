import graphene
import graphql_jwt
from datetime import datetime
from graphql_jwt.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils.translation import activate
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from profiles.models import Profile
from dynamic_preferences.users.models import UserPreferenceModel

class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'avatar', 'date_of_birth', 'country', 'telegram_username']


class FieldType(graphene.ObjectType):
    class Meta:
        description = 'Form field'

    input_type = graphene.String()

    def resolve_input_type(root, info, **kwargs):
        return root['input_type']


class PreferencesType(DjangoObjectType):
    section = graphene.String()
    name = graphene.String()
    value = graphene.String()
    verbose_name = graphene.String()
    help_text = graphene.String()
    field = graphene.Field(FieldType)
    class Meta:
        model = UserPreferenceModel
        exclude = ['id', 'instance', 'raw_value']

    def resolve_field(root, info, **kwargs):
        return root.preference.get_api_field_data()


class UserType(DjangoObjectType):
    profile = graphene.Field(ProfileType)
    preferences = graphene.List(PreferencesType)
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'phone', 'locale']

    @classmethod
    def resolve_preferences(cls, root, info, **kwargs):
        return UserPreferenceModel.objects.filter(instance=info.context.user)


class ObtainJSONWebToken(graphql_jwt.JSONWebTokenMutation):
    user = graphene.Field(UserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        return cls(user=info.context.user)


class Query(graphene.ObjectType):
    viewer = graphene.Field(UserType)
    preferences = graphene.List(PreferencesType, language=graphene.String())

    @login_required
    def resolve_viewer(self, info, **kwargs):
        return info.context.user

    @login_required
    def resolve_preferences(self, info, language=None, **kwargs):
        if (language):
            activate(language)
        return UserPreferenceModel.objects.filter(instance=info.context.user)


class UserInput(graphene.InputObjectType):
    avatar = graphene.String()
    firstName = graphene.String()
    lastName = graphene.String()
    dateOfBirth = graphene.String()
    username = graphene.String()
    email = graphene.String(required=True)
    phone = graphene.String()
    country = graphene.String()
    telegramUsername = graphene.String()


class UpdateProfile(graphene.Mutation):
    class Arguments:
        input = UserInput(required=True)

    ok = graphene.Boolean()
    user = graphene.Field(UserType)

    @staticmethod
    @login_required
    def mutate(root, info, input=None):
        ok = True
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication credentials were not provided")
        user.username = input.username
        user.email = input.email
        user.phone = input.phone
        user.save()

        if not input.avatar:
            user.profile.avatar = ''
        user.profile.first_name = input.firstName
        user.profile.last_name = input.lastName
        user.profile.date_of_birth = datetime.strptime(input.dateOfBirth, '%Y-%m-%d')
        user.profile.country = input.country
        user.profile.telegram_username = input.telegramUsername
        user.profile.save()
        return UpdateProfile(user=user, ok=ok)


class ItemPreference(graphene.InputObjectType):
    section = graphene.String(required=True)
    name = graphene.String(required=True)
    value = graphene.String(required=True)


class UpdatePreferences(graphene.Mutation):
    class Arguments:
        input = graphene.List(ItemPreference, required=True)

    ok = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, input=None):
        ok = True
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication credentials were not provided")
        for item in input:
            key = item.section + '__' + item.name
            user.preferences[key] = item.value == 'true'
        return UpdatePreferences(ok=ok)
    

class UploadPhoto(graphene.Mutation):
    class Arguments:
        file = Upload(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, file=None, **kwargs):
        # profile = Profile.objects.get(user=info.context.user)
        # profile.avatar = file
        # profile.save()
        return UploadPhoto(ok=True)


class Mutation(graphene.ObjectType):
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()
    
    update_profile = UpdateProfile.Field()
    update_preferences = UpdatePreferences.Field()
    upload_photo = UploadPhoto.Field()
