from rest_framework import generics, status
from rest_framework.response import Response
from .models import ReceivedMessage, User, UserProfile, UserDetails, UserDescription
from .serializers import ReceivedMessageSerializer, UserSerializer, UserProfileSerializer
from django.core.cache import cache
from datetime import timedelta
from django.utils import timezone

class MessageReceiveView(generics.CreateAPIView):
    serializer_class = ReceivedMessageSerializer

    def create(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        message = request.data.get('message')

        user, created = User.objects.get_or_create(phone_number=phone_number)

        # Process the message and determine the response based on user registration status and message content
        response_data = {}

        if message.lower() == 'penzi' and not user.is_registered:
            response_data['status'] = 'Welcome to our dating service with 6000 potential dating partners! ' \
                                      'To register SMS start#name#age#gender#county#town to 22141. E.g., ' \
                                      'start#John Doe#26#Male#Nakuru#Naivasha'
        elif message.lower() == 'penzi' and user.is_registered:
            response_data['status'] = 'You are registered for dating. To search for a MPENZI, SMS match#age#town ' \
                                      'to 22141 and meet the person of your dreams. E.g., match#23-25#Nairobi'
        elif message.lower().startswith('start#') and not user.is_registered:
            # Extract information from the message for UserProfile
            try:
                _, name, age, gender, county, town = message.split('#')
            except ValueError:
                return Response("Invalid format. Please provide information in the format 'start#name#age#gender#county#town'", status=400)

            # Create UserProfile instance
            profile = UserProfile.objects.create(
                user=user,
                name=name,
                age=age,
                gender=gender,
                county=county,
                town=town
            )

            # Set user as registered
            user.is_registered = True
            user.save()

            # Serialize the UserProfile instance to get the username
            profile_serializer = UserProfileSerializer(profile)
            username = profile_serializer.data.get('name', '')

            response_data['status'] = f"Your profile has been created successfully {username}. " \
                                      "SMS details#levelOfEducation#profession#maritalStatus#religion#ethnicity " \
                                      "to 22141. E.g. details#diploma#driver#single#christian#mijikenda"

        elif message.lower().startswith('details#') and user.is_registered:
            # Extract information from the message for UserDetails
            try:
                _, level_of_education, profession, marital_status, religion, ethnicity = message.split('#')
            except ValueError:
                return Response("Invalid format. Please provide information in the format 'details#level_of_education#profession#marital_status#religion#ethnicity'", status=400)

            # Create UserDetails instance
            user_details = UserDetails.objects.create(
                user=user,
                level_of_education=level_of_education,
                profession=profession,
                marital_status=marital_status,
                religion=religion,
                ethnicity=ethnicity
            )

            # Set timeout for the user after 'details' message (1 minute timeout)
            cache.set(f'user_{user.id}_last_details', timezone.now())

            response_data['status'] = f"This is the last stage of registration. " \
                                      "SMS a brief description of yourself to 22141 starting with the word " \
                                      "MYSELF." \
                                      "E.g., MYSELF chocolate, lovely, sexy etc."

        ReceivedMessage.objects.create(user=user, message=message)
        
        # Check for timeout and send another response if needed
        last_details_time = cache.get(f'user_{user.id}_last_details')
        if last_details_time:
            time_difference = timezone.now() - last_details_time
            if time_difference.total_seconds() > 60:  # Check if one minute has passed since 'details' message
                # Send a timeout response if one minute has elapsed since 'details' message
                response_data['status'] = f"You were registered for dating with your initial details. " \
                                          "To search for a MPENZI, SMS match#age#town " \
                                          "to 22141 and meet the person of your dreams. " \
                                          "E.g., match#23-25#Nairobi"
                # Clear the 'last_details' cache as timeout occurred
                cache.delete(f'user_{user.id}_last_details')
        
        elif message.lower().startswith('myself ') and user.is_registered:
                    # Extract user description
                    description = message.split(' ', 1)[1]

                    # Create or update user description
                    user_description, created = UserDescription.objects.get_or_create(user=user)
                    user_description.description_text = description
                    user_description.save()

                    response_data['status'] = f"You are now registered for dating. " \
                                               "To search for a MPENZI, SMS match#age#town to 22141 and meet the person of your dreams. " \
                                               "E.g., match#23-25#Nairobi"
        # Handling 'match#' message for matches and the first three matches separately
        if message.lower().startswith('match#') and user.is_registered:
            try:
                _, age_range, county = message.split('#')
                min_age, max_age = map(int, age_range.split('-'))
            except ValueError:
                return Response("Invalid format. Please provide information in the format 'match#age_range#county'", status=400)

            if user.profile.gender.lower() == 'female':
                gender_filter = 'male'
                gender_display = 'gentlemen'
                gender_type = 'man'
            else:
                gender_filter = 'female'
                gender_display = 'ladies'
                gender_type = 'lady'

            matching_users = UserProfile.objects.filter(
                age__gte=min_age,
                age__lte=max_age,
                county__iexact=county,
                gender__iexact=gender_filter,
                user__is_registered=True
            )

            matching_users_count = matching_users.count()

            response_data['status'] = f"We have {matching_users_count} {gender_display} who match your choice! "

            if matching_users_count > 0:
                response_data['status'] += f"To get more details about a {gender_type}, SMS the match number e.g., 0722010203 to 22141"

            ReceivedMessage.objects.create(user=user, message=message)

            # Send the initial response about matches
            return Response(response_data)

        elif message.lower() == 'next' and user.is_registered:
            displayed_matches_key = f"displayed_matches_{user.id}"
            displayed_matches = cache.get(displayed_matches_key, [])

            remaining_matches = UserProfile.objects.filter(
                user__is_registered=True
            ).exclude(user__id__in=displayed_matches)

            response_data = {}

            if len(remaining_matches) > 0:
                next_three_matches = remaining_matches[:3]

                if next_three_matches:
                    response_data['status'] = "Here are the next three matches:\n"
                    for match in next_three_matches:
                        match_info = f"Name: {match.name}, Age: {match.age}, Phone Number: {match.user.phone_number}"
                        response_data['status'] += f"{match_info}\n"
                        displayed_matches.append(match.user_id)

                    cache.set(displayed_matches_key, displayed_matches)
                else:
                    response_data['status'] = "There are no more matches available at the moment. Try again later."
            else:
                response_data['status'] = "There are no more matches available at the moment. Try again later."

            ReceivedMessage.objects.create(user=user, message=message)

            # Send the response for the 'next' message
            return Response(response_data)
        
        elif message.isdigit() and len(message) == 10:  # Check if it's a match number
                match_phone_number = message
                # Retrieve match details
                match_profile = UserProfile.objects.filter(user__phone_number=match_phone_number).first()

                if match_profile:
                    user_description = UserDescription.objects.filter(user=match_profile.user).first()
                    if user_description:
                        match_description = user_description.description_text
                    else:
                        match_description = "No description available."
                        
                    response_data['status'] = f"{match_profile.name} aged {match_profile.age}, {match_profile.county} County, {match_profile.town} town, " \
                                            f"{match_profile.level_of_education}, {match_profile.profession}, {match_profile.marital_status}, " \
                                            f"{match_profile.religion}, {match_profile.ethnicity}. Send DESCRIBE {match_phone_number} to get more details about {match_profile.name}."
                    
                    # Cache the match ID and user ID
                    cache.set(f"match_user_{match_profile.user.id}_interested_in_{user.id}", True)
                    cache.set(f"user_{user.id}_interested_in_match_{match_profile.user.id}", True)

                    ReceivedMessage.objects.create(user=user, message=message)

                    return Response(response_data)

        elif message.isdigit() and (len(message) == 10 or len(message) == 9):  # Check if it's a match number (10 or 9 digits)
            match_phone_number = message.zfill(10)  # Pad the number with zeros if necessary
            # Retrieve match details
            match_profile = UserProfile.objects.filter(user__phone_number=match_phone_number).first()

            if match_profile:
                user_description = UserDescription.objects.filter(user=match_profile.user).first()
                if user_description:
                    match_description = user_description.description_text
                else:
                    match_description = "No description available."
                    
                response_data['status'] = f"{match_profile.name} aged {match_profile.age}, {match_profile.county} County, {match_profile.town} town, " \
                                          f"{match_profile.level_of_education}, {match_profile.profession}, {match_profile.marital_status}, " \
                                          f"{match_profile.religion}, {match_profile.ethnicity}. Send DESCRIBE {match_phone_number} to get more details about {match_profile.name}."
                
                # Cache the match ID and user ID
                cache.set(f"match_user_{match_profile.user.id}_interested_in_{user.id}", True)
                cache.set(f"user_{user.id}_interested_in_match_{match_profile.user.id}", True)

                ReceivedMessage.objects.create(user=user, message=message)

                return Response(response_data)

        elif message.lower().startswith('describe') and len(message.split()) == 2 and user.is_registered:
            _, match_phone_number = message.split()
            match_phone_number = match_phone_number.strip()

            match_profile = UserProfile.objects.filter(user__phone_number=match_phone_number).first()

            if match_profile:
                user_description = UserDescription.objects.filter(user=match_profile.user).first()
                if user_description:
                    match_description = user_description.description_text
                else:
                    match_description = "No description available."

                response_data['status'] = f"{match_profile.name} describes herself as {match_description}"
                
                # Check if the user is interested in this match
                user_interested = cache.get(f"user_{user.id}_interested_in_match_{match_profile.user.id}", False)
                if user_interested:
                    response_data['status'] += f"\nSend YES to 22141 if you want to know more about {match_profile.name}."
                else:
                    response_data['status'] += f"\nYou have not shown interest in {match_profile.name}."
                    
                ReceivedMessage.objects.create(user=user, message=message)

                return Response(response_data)

        elif message.lower() == 'yes' and user.is_registered:
            interested_match_id = None
            cache_keys = cache._cache.keys()  

            for key in cache_keys:
                if key.startswith(f"user_{user.id}_interested_in_match_"):
                    interested_match_id = key.split('_')[-1]
                    break

            if interested_match_id:
                match_profile = UserProfile.objects.filter(user__id=interested_match_id).first()
                match_interested_user = cache.get(f"match_user_{match_profile.user.id}_interested_in_{user.id}", False)

                if match_interested_user:
                    response_data['status'] = f"Hi {match_profile.name}, a man called {user.profile.name} is interested in you and requested your details. " \
                                            f"He is aged {user.profile.age} based in {user.profile.county}. Do you want to know more about him? " \
                                            f"Send YES to 22141."

                    # Clear the interest cache for both users
                    cache.delete(f"match_user_{match_profile.user.id}_interested_in_{user.id}")
                    cache.delete(f"user_{user.id}_interested_in_match_{match_profile.user.id}")

                    ReceivedMessage.objects.create(user=user, message=message)

                    return Response(response_data)
        return Response(response_data)


    
class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        
        # Check if a user with the provided phone number already exists
        existing_user = User.objects.filter(phone_number=phone_number).first()
        if existing_user:
            serializer = self.get_serializer(existing_user)
            return Response(serializer.data, status=status.HTTP_409_CONFLICT)  # Return conflict status code
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

