from django.test import TestCase
from django.urls import reverse
from apps.accounts.models import User
from apps.innovation.models import Idea, IdeaComment, IdeaVote

class InnovationTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username='innovator', email='inno@test.com', password='pass', role=User.Role.STUDENT)
        self.client.login(username='innovator', password='pass')

    def test_create_idea(self):
        response = self.client.post(reverse('innovation:create'), {
            'title': 'AI Automated Recycling',
            'category': 'Sustainability',
            'problem': 'Improper waste segregation causes landfill toxicity.',
            'solution': 'Computer vision conveyor sorter.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Idea.objects.filter(title='AI Automated Recycling').exists())

    def test_idea_voting_toggle(self):
        idea = Idea.objects.create(author=self.student, title='Bio-degradable Circuit', problem='e-waste', solution='cellulose substrate')
        # Vote
        self.client.get(reverse('innovation:vote', args=[idea.id]))
        self.assertEqual(IdeaVote.objects.filter(idea=idea, user=self.student).count(), 1)
        # Toggle off
        self.client.get(reverse('innovation:vote', args=[idea.id]))
        self.assertEqual(IdeaVote.objects.filter(idea=idea, user=self.student).count(), 0)
