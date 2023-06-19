from django import forms

from .places import DISTRICT_CHOICES, STATE_CHOICES
from .models import NewsResponse
from django.utils.safestring import mark_safe



# class to allow for placeholder in districts field
class CustomSelect(forms.widgets.Select):
    def __init__(self, attrs=None, choices=(), modify_choices=()):
        super(CustomSelect, self).__init__(attrs, choices=choices)
        # set data
        self.modify_choices = modify_choices

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super(CustomSelect, self).create_option(
            name, value, label, selected, index, subindex, attrs
        )
        # hide all optgroups
        if value == "":
            option["attrs"]["disabled"] = ""
            option["attrs"]["selected"] = ""
            option["attrs"]["hidden"] = ""
        return option


class NewsResponseForm(forms.ModelForm):
    # news_Response = forms.IntegerField(
    #     label="Please report your belief about the accuracy of the post (in percentage):",
    #     widget=forms.NumberInput(attrs={"min": 0, "max": 100, "class": "lead"}),
    # )
    # Added by Ranjeet
    news_Response = forms.TypedChoiceField(
        label="Please report your belief about the accuracy of the post :",
        coerce=lambda x: x == 'True',
        choices=((True, 'True'),(False, 'False')),
        widget=forms.RadioSelect() 
    )

    class Meta:
        model = NewsResponse
        fields = ["news_Response"]


class QuizForm(forms.Form):
    q1 = forms.IntegerField(
        label="1. If you're running a race and you pass the person in second place, what place are you in?",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    q2 = forms.IntegerField(
        label="2. A farmer had 15 sheep and all but 8 died. How many are left?",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    q3 = forms.IntegerField(
        label="3. If it takes 2 nurses 2 minutes to check 2 patients, how many minutes does it take 40 nurses to check 40 patients?",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
    )


class DemocraticOpinionForm1(forms.Form):
    NEWS_CHOICES = [
        ("social media", "Social Media"),
        ("television", "Television"),
        ("newspaper", "Newspaper"),
        ("online news portals", "Online News Portals"),
    ]
    news_source = forms.ChoiceField(
        choices=NEWS_CHOICES,
        widget=forms.RadioSelect(),
        label="1. What is your primary source of news?",
    )

    affiliation = forms.ChoiceField(
        choices=[("True", "Yes"), ("False", "No")],
        widget=forms.RadioSelect(),
        label="2. Are you affiliated/associated with any political party?",
    )

    DEMOCRATIC_CHOICES = [
        (0, "Strongly Dislike;"),
        (25, "Dislike"),
        (50, "Neither Like nor Dislike"),
        (75, "Like"),
        (100, "Strongly Like"),
    ]
    democratic_Opinion = forms.ChoiceField(
        choices=DEMOCRATIC_CHOICES,
        widget=forms.RadioSelect(),
        # label="3. Please report your level of approval for the politics and policies of PM Narendra Modi on the following scale:",
        label= mark_safe("3. Some people like PM Narendra Modi as a leader and some don't like him. What about you - do you like Modi or you <br> dislike him?")
    )
    


class DemocraticOpinionForm2(forms.Form):
    age = forms.IntegerField(
        label="1. What is your age (in years)?",
        min_value=18,
        max_value=100,
    )

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
        ("na", "Prefer not to say"),
    ]
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.RadioSelect(),
        label="2. What is your gender?",
    )

    RELIGION_CHOICES = [
        ("hinduism", "Hinduism"),
        ("islam", "Islam"),
        ("christianity", "Christianity"),
        ("sikhism", "Sikhism"),
        ("jainism", "Jainism"),
        ("na", "No religion"),
        ("other", "Other"),
    ]
    religion = forms.ChoiceField(
        choices=RELIGION_CHOICES,
        widget=forms.RadioSelect,
        label="3. What is your religion?",
    )

    state = forms.ChoiceField(
        choices=STATE_CHOICES,
        widget=forms.Select(),
        label="4. In which state was your high school located in?",
    )

    district = forms.ChoiceField(
        choices=DISTRICT_CHOICES,
        widget=CustomSelect(modify_choices=tuple(DISTRICT_CHOICES)),
        label="5. In which district was your high school located in?",
    )

    HIGHSCHOOL_CHOICES = [
        ("private", "Private"),
        ("central government", "Central Government"),
        ("state government", "State Government"),
    ]
    highschool = forms.ChoiceField(
        choices=HIGHSCHOOL_CHOICES,
        widget=forms.RadioSelect(),
        label="6. What best describes your high school?",
    )

    EDUCATION_CHOICES = [
        ("high school", "High school"),
        ("Undergraduate", "Undergraduate"),
        ("graduate", "Graduate"),
        ("doctorate", "Doctorate"),
    ]
    edu_level = forms.ChoiceField(
        choices=EDUCATION_CHOICES,
        widget=forms.RadioSelect(),
        label="7. What is your highest level of education? (please include any course you are currently pursuing)",
    )

    COURSE_CHOICES = [
        ("science", "Science"),
        ("social science", "Social Science"),
        ("humanities and languages", "Humanities and Languages"),
        ("Engineering", "Engineering"),
        ("medical", "Medical"),
        (
            "professional degrees like law/management",
            "Professional degrees like law/management",
        ),
        ("other", "Other"),
    ]
    course = forms.ChoiceField(
        choices=COURSE_CHOICES,
        widget=forms.RadioSelect(),
        label="8. What best describes your undergraduate course?",
    )

    CHECKER_CHOICES = [
        ("a great deal", "A Great Deal"),
        ("a lot", "A lot"),
        ("a moderate amount", "A Moderate Amount"),
        ("a little", "A little"),
        ("na", "None at all"),
    ]
    checker = forms.ChoiceField(
        choices=CHECKER_CHOICES,
        widget=forms.RadioSelect(),
        label="9. Please, choose the answer 'A little' below.",
    )

    voted = forms.ChoiceField(
        choices=[("True", "Yes"), ("False", "No")],
        widget=forms.RadioSelect(),
        label="10. Have you voted for Lok Sabha or State Assembly elections in the last 5 years?",
    )

    APPS_CHOICES = [
        ("whatsapp", "WhatsApp"),
        ("facebook", "Facebook"),
        ("instagram", "Instagram"),
        ("twitter", "Twitter"),
        ("youtube", "YouTube"),
        ("reddit", "Reddit"),
        ("snapchat", "Snapchat"),
        ("telegram", "Telegram"),
        ("signal", "Signal"),
        ("none", "None"),
    ]
    social_media_apps = forms.MultipleChoiceField(
        choices=APPS_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        label="11. What social media apps do you use regularly?",
    )

    TIME_CHOICES = [
        ("less than 30 minutes", "Less than 30 minutes"),
        ("30-60 minutes", "30-60 minutes"),
        ("1-2 hours", "1-2 hours"),
        ("3-5 hours", "3-5 hours"),
        ("more than 5 hours", "More than 5 hours"),
    ]
    time_spent = forms.ChoiceField(
        choices=TIME_CHOICES,
        widget=forms.RadioSelect(),
        label="12. How much time do you spend on social media every day (average)?",
    )

    SOCIAL_MEDIA = [
        ("whatsapp", "WhatsApp"),
        ("facebook", "Facebook"),
        ("instagram", "Instagram"),
        ("twitter", "Twitter"),
        ("youtube", "YouTube"),
        ("reddit", "Reddit"),
        ("social media- other", "Other"),
        ("social media- na", "None"),
    ]

    source_social_media = forms.MultipleChoiceField(
        choices=SOCIAL_MEDIA,
        widget=forms.CheckboxSelectMultiple(),
        label= mark_safe(
        """13. In the recent past, what sources have you used to follow the news? (Choose all that apply)<br/>
        a. Social Media""",
        )
    )

    
    TV_NEWS_CHANNELS = [
        ("ndtv", "NDTV"),
        ("aaj tak", "Aaj Tak"),
        ("times now", "Times Now"),
        ("republic", "Republic"),
        ("sudarshan news", "Sudarshan News"),
        ("zee news", "Zee News"),
        ("tv news channels- other", "Other"),
        ("tv news channels- na", "None"),
    ]
    source_news_channels = forms.MultipleChoiceField(
        choices=TV_NEWS_CHANNELS,
        widget=forms.CheckboxSelectMultiple(),
        label="b. TV News Channels",
    )

    ONLINE_NEWS_BLOGS = [
        ("quint", "Quint"),
        ("newslaundry", "Newslaundry"),
        ("swarajya", "Swarajya"),
        ("opindia", "OpIndia"),
        ("scoopwhoop", "ScoopWhoop"),
        ("wire", "Wire"),
        ("online news portals- other", "Other"),
        ("online news portals- na", "None"),
    ]
    source_online_news_blogs = forms.MultipleChoiceField(
        choices=ONLINE_NEWS_BLOGS,
        widget=forms.CheckboxSelectMultiple(),
        label="c. Online News Portals/Blogs",
    )

    NEWSPAPERS = [
        ("dainik jagran", "Dainik Jagran"),
        ("dainik bhaskar", "Dainik Bhaskar"),
        ("hindustan times", "Hindustan Times"),
        ("amar ujala", "Amar Ujala"),
        ("times of india", "Times of India"),
        ("the hindu", "The Hindu"),
        ("indian express", "Indian Express"),
        ("newspapers- other", "Other"),
        ("newspapers- na", "None"),
    ]

    source_newspapers = forms.MultipleChoiceField(
        choices=NEWSPAPERS,
        widget=forms.CheckboxSelectMultiple(),
        label="d. Newspapers",
    )

    
    # sources = forms.MultipleChoiceField(
    #     choices=SOURCES_CHOICES,
    #     required= True,
    #     widget=forms.CheckboxSelectMultiple(),
    #     label="13. In the recent past, what sources have you used to follow the news? (Choose all that apply)",
    # )

    sm_other = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={"hidden": ""}),
        required=False,
    )

    tv_other = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={"hidden": ""}),
        required=False,
    )

    onp_other = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={"hidden": ""}),
        required=False,
    )

    np_other = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={"hidden": ""}),
        required=False,
    )


class UPIIDForm(forms.Form):
    upi_ID = forms.CharField(max_length=50)


class StartSurveyForm(forms.Form):
    consent = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="I consent to participate: ",
    )

    upi_ID = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your UPI ID",
                "class": "form-control",
            }
        ),
    )

    upi_ID_domain = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your UPI Domain",
                "class": "form-control",
            }
        ),
    )


class NewsAccuracyTaskForm(forms.Form):
    pass


class NewsResponseInfoForm(forms.Form):
    pass

# Added by Ranjeet
class EarningForm(forms.Form):
    pass
