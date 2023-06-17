from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from ordered_model.models import OrderedModel

from educa.apps.core.models import ContentBase, CreatorBase, TimeStampedBase
from educa.apps.course.models import Course
from educa.apps.module.models import Module


class Quiz(ContentBase, TimeStampedBase, OrderedModel):
    """
    Este modelo representa um quiz de multipla escolha sobre o tema do módulo.

    Fields:
        pass_percent (float): A porcentagem de 0 a 100 que o usuário precisa acertar para concluir o teste.
        order (int): representa a sua ordem crescente dentro do módulo, a qual é definida automáticamente.
    """

    pass_percent = models.PositiveIntegerField(
        validators=[MaxValueValidator(100)]
    )
    module = models.ForeignKey(
        Module,
        related_name='quizzes',
        on_delete=models.CASCADE,
    )
    course = models.ForeignKey(
        Course,
        related_name='quizzes',
        on_delete=models.CASCADE,
    )

    order_with_respect_to = ('course', 'module')

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'Quiz({self.title}) - Course({self.course_id})'


class QuizQuestion(TimeStampedBase, OrderedModel):
    """
    Este modelo representa cada pergunta e resposta de um objeto Quiz.

    Fields:
        feedback (str): Observação ou comentário sobre a questão.
        answers (list[str]): Lista que armazena as respostas verdadeiras e falsas.
        time_in_minutes (int): = Tempo para responder à questão (0 se não tiver tempo).
        correct_response (int): =  Index da resposta correta na lista 'answers'.
    """

    question = models.TextField()
    feedback = models.TextField()
    answers = ArrayField(models.TextField())
    time_in_minutes = models.FloatField(default=0)
    correct_response = models.IntegerField()
    quiz = models.ForeignKey(
        Quiz, related_name='questions', on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course,
        related_name='questions_quiz',
        on_delete=models.CASCADE,
    )

    order_with_respect_to = 'quiz'

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        try:
            self.answers[self.correct_response]
        except IndexError:
            raise ValidationError(
                f'invalid correct_response the response must between in array index (0-{len(self.answers) - 1}).'
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f'QuizQuestion({self.id}) - Quiz({self.quiz_id})'


class QuizRelation(CreatorBase, TimeStampedBase):
    """
    Este modelo representa o status do usuário com o quiz.
    """

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('creator', 'quiz'), name='unique quiz relation'
            )
        ]

    def __str__(self):
        return f'QuizRelation({self.creator}) - Quiz({self.quiz_id})'
