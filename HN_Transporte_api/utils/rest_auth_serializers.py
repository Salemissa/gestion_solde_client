# from dj_rest_auth.serializers
# from dj_rest_auth.views
from rest_framework import serializers, status
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import SetPasswordForm
from dj_rest_auth.app_settings import api_settings
from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.utils import email_address_exists, get_username_max_length
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from HN_Transporte_api.models import User
import logging



logger = logging.getLogger(__name__)



class UserSerializer(serializers.ModelSerializer):
    # poste = PosteSerializer()
    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    class Meta:
        model = User
        fields = ['id', 'username', 'email''first_name', 'last_name', 'phone', 'watsapp',]      
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')  

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=get_username_max_length(),
        min_length=allauth_settings.USERNAME_MIN_LENGTH,
        required=allauth_settings.USERNAME_REQUIRED,
    )
    email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    phone = serializers.CharField(required=False)
    watsapp = serializers.CharField(required=False)
    
    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _('Un utilisateur est déjà enregistré avec cette adresse e-mail.'),
                )
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("Le deux mot de passe ne sont pas identique."))
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'watsapp': self.validated_data.get('watsapp', None),
            'phone': self.validated_data.get('phone', None),
           
        }
      
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2','watsapp', 'phone',)
        
        
    def save(self, request):
        
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        try:
            adapter.clean_password(self.cleaned_data['password1'], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                detail=serializers.as_serializer_error(exc)
            )
        # if not groups or groups == []:
        #     raise serializers.ValidationError({'groups': _('un utilisateur doit avoir au moins un groupe.'),}, code=status.HTTP_400_BAD_REQUEST)
        
        user.phone = self.cleaned_data['phone']
        # user.poste = self.cleaned_data['poste']
        user.is_superuser = True
       
        user.save()
        # user.groups.set(groups)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user          
class UserEditSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    class Meta:
        
        model = User
        fields = ('id',  'is_active', 'username', 'email', 'phone', 'watsapp',)
        read_only_fields = ('id', 'username',)      

class UserEditGetSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    # poste = PosteSerializer()
    class Meta:
        
        model = User
        fields = ('id',  'is_active', 'username', 'email', 'phone', 'watsapp',)
        read_only_fields = ('id', 'username',)  
class UserGetSerializer(serializers.ModelSerializer):
    # poste = PosteSerializer()
    class Meta:
        model = User
        fields = ('id', 'is_active', 'username', 'email','phone', 'watsapp',)

class AdminPasswordEditSerializer(serializers.Serializer):
    # old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    set_password_form_class = SetPasswordForm
    set_password_form = None
    
    def __init__(self, *args, **kwargs):
        self.logout_on_password_change = api_settings.LOGOUT_ON_PASSWORD_CHANGE
        super().__init__(*args, **kwargs)
        self.request = self.context.get('request')
        self.user = self.instance
        self.instance = None

    def custom_validation(self, attrs):
        pass
    
    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs,
        )
        self.custom_validation(attrs)
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(self.request, self.user)
        
class JWTSerializer(serializers.Serializer):
    """
    Serializer for JWT authentication.
    """
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
   

class MyTokenObtainSlidingSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):

            
        # posts = Poste.objects.filter(users=user)
       
        # posts_list = LocaliteGetAgentSerializer(Localite.objects.filter(poste=posts[0]),many=True).data
        # print(posts_list)

        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['phone'] = user.phone
        token['watsapp'] = user.watsapp
        # token['groups'] = user.get_groups()
        # token['poste'] = posts_list
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        
        
        return token
    

           