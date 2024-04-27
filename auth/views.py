import os

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings

from .schemas import SignupSchema, SigninSchema, InitializeResetPasswordSchema, ResetPasswordSchema
from home.models import Users, Password, Subscription, ResetPassword

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from jwcrypto import jwt, jwk

from datetime import datetime

import base64

# Create your views here.
@csrf_exempt
def signup(request):

    if request.method == 'POST':
        
        try:

            # Chargement du shemas d'inscription
            schema = SignupSchema()

            # Traitement des données d'inscription à l'aide du shemas
            result = schema.load(request.POST)
            
            # Créer un objet de hachage SHA-256
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())

            # Mettre à jour le hachage avec le mot de passe
            digest.update(result["password"].encode('utf-8'))

            # Finaliser le hachage
            hash_bytes = digest.finalize()

            # Encoder le hachage en base64
            hash_base64 = base64.b64encode(hash_bytes).decode('utf-8')

            # Chargeent du plan de subscription gratuit pour les nouveaux utilisateurs
            free_subscription = Subscription.objects.get(name="Free Plan")

            # Creation de l'objet utilisateur
            user = Users.objects.create(
                email=result["email"],
                full_name=result["full_name"],
                is_staff=False,
                subscription=free_subscription
            )

            # Sauvegarde de l'objet utilisateur en db
            user.save()

            # # Creation de l'objet password
            password = Password.objects.create(
                password=hash_base64,
                user=user
            )

            # Sauvegarde de l'objet password en db
            password.save()

            # Retourne cette ligne si l'utilisateur est crée avec success
            return JsonResponse({'message': 'User created successfully'}, status=201)

        except ValidationError as err:

            # Retourne cette ligne si une erreur est rencontrée lors de la construction du shemas d'inscription
            return JsonResponse(err.messages, status=400)

    # Retourne cette ligne si la méthode appelé est autre que POST
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def signin(request):

    if request.method == 'POST':

        try:

            # Chargement du shemas de connexion
            schema = SigninSchema()

            # Traitement des données de connexion à l'aide du shemas
            result = schema.load(request.POST)

            # Nous allons récuperer l'utilisateur avec la même adress email fourni pour la connexion
            user = Users.objects.get(email=result["email"])

            # Nous allons récuperer le mot de passe de l'utilisateur avec la même adress email fourni pour la connexion
            password = Password.objects.get(user=user)

            # Nous allons récuperer le mot de passe de l'utilisateur en question depuis la db
            db_password_str = password.password

            # Créer un objet de hachage SHA-256
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())

            # Mettre à jour le hachage avec le mot de passe
            digest.update(result["password"].encode('utf-8'))

            # Finaliser le hachage
            hash_bytes = digest.finalize()

            # Encoder le hachage en base64
            hash_base64 = base64.b64encode(hash_bytes).decode('utf-8')

            # Nous comparons le mot de passe de la db avec celui fourni lors de la connexion
            if db_password_str == hash_base64:

                # Nous récuperons la clé privé pour signer notre token
                key = jwk.JWK.from_pem(settings.PRIVATE_KEY)

                # Nous calculons la datetime d'émission de notre token
                iat = int(datetime.now().timestamp())

                # Nous calculons la datetime d'expiration de notre token en prenant en compte la validité de la subscription acheté par notre utilisateur
                exp = iat + (user.subscription.validity_duration * 86400)

                # Nous fournissons un header ansi qu'un payload  a notre token
                token = jwt.JWT(header={"alg": "RS256", "typ": "JWT"}, claims={"iss": "xana-web", "sub": user.pk, "exp": exp, "iat": iat, "name": user.full_name, "admin": user.is_staff})
                
                # Nous signons notre token avec la clé privé
                token.make_signed_token(key)

                # Retourne cette ligne si l'utilisateur se connecte avec success
                return JsonResponse({'message': 'Signin successful', "token": token.serialize()}, status=200)
            
            # Dans le cas ou le mot de passe en db ne correspond pas a celui fourni par l'utilisateur lors de la connexion
            else:
                
                # Ici nous lèvons l'exception pour renvoyer le message adéquat
                raise

        except:

            # Retourne cette ligne si une erreur est rencontrée lors de la construction du shemas d'inscription
            return JsonResponse({'message': 'Invalid credentials'}, status=400)

    # Retourne cette ligne si la méthode appelé est autre que POST
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def initialize_reset_password(request):

    if request.method == 'POST':

        try:

            # Chargement du shemas de reset_password
            schema = InitializeResetPasswordSchema()

            # Traitement des données de reset_password à l'aide du shemas
            result = schema.load(request.POST)

            # Nous créons une boucle pour vérifié l'authenticité du token générer
            while True:

                # Générer une chaîne de caractères aléatoire
                token_bytes = os.urandom(16)  # 16 octets pour une chaîne de 32 caractères hexadécimaux
                token = base64.urlsafe_b64encode(token_bytes).decode()

                # Nous vérifions que le token crée n'existe pas dans la db
                if not ResetPassword.objects.filter(token=token).exists():

                    # Nous récuperons l'utilisateur à qui appartient l'adress email
                    user = Users.objects.get(email=result["email"])

                    # Nous calculons l'expiration du token pour aléger la db
                    exp_datetime = datetime.fromtimestamp(datetime.now().timestamp() + 30 * 60)

                    # Nous créons l'objet reset_password
                    rp = ResetPassword.objects.create(user=user, token=token, expiration_date=exp_datetime)

                    # Nous sauvegardons l'objet en db
                    rp.save()

                    # Send Email

                    break

            # Retourne cette ligne si l'utilisateur réussi la procédure de réinitialisation de mot de passe
            return JsonResponse({'message': 'The password reset procedure has been initiated'}, status=200)

        except:

            # Retourne cette ligne si une erreur est rencontrée lors de la construction du shemas de reset_password
            return JsonResponse({'message': 'Invalid email'}, status=400)

    # Retourne cette ligne si la méthode appelé est autre que POST
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def reset_password(request, token):

    if request.method == 'POST':

        try:

            if ResetPassword.objects.filter(token=token).exists():

                rp = ResetPassword.objects.get(token=token)

                # Datetime actuelle
                now = datetime.now()

                # Vérifier si la date est passée
                if rp.expiration_date > now:
                    
                    # Chargement du shemas de reset_password
                    schema = ResetPasswordSchema()

                    # Traitement des données de reset_password à l'aide du shemas
                    result = schema.load(request.POST)

                    # Créer un objet de hachage SHA-256
                    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())

                    # Mettre à jour le hachage avec le mot de passe
                    digest.update(result["password"].encode('utf-8'))

                    # Finaliser le hachage
                    hash_bytes = digest.finalize()

                    # Encoder le hachage en base64
                    hash_base64 = base64.b64encode(hash_bytes).decode('utf-8')
                    
                    # Changement du password
                    Password.objects.filter(user=rp.user).update(password=hash_base64)

                    # Suppression du token après modification
                    rp.delete()

                    # Retourne cette ligne si l'utilisateur saisi une adress email valide pour lequel reset le password
                    return JsonResponse({'message': 'The password has been reset successfully.'}, status=200)

                return JsonResponse({'message': 'The password reset token has expired. Please generate a new one.'}, status=403)

            return JsonResponse({'message': 'The password reset token does not exist.'}, status=404)

        except ValidationError as err:

            # Retourne cette ligne si une erreur est rencontrée lors de la construction du shemas de reset_password
            return JsonResponse(err.messages, status=400)

    # Retourne cette ligne si la méthode appelé est autre que POST
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def get_public_key(request):

    if request.method == 'GET':

        return JsonResponse({'message': 'Public key shared successfully.', 'key': settings.PUBLIC_KEY.decode('utf-8')}, status=200)

    # Retourne cette ligne si la méthode appelé est autre que GET
    return JsonResponse({'error': 'Method not allowed'}, status=405)