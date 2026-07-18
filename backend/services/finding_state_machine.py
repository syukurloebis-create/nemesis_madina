from enum import Enum


class FindingStatus(str, Enum):

    DRAFT = "DRAFT"

    UNDER_REVIEW = "UNDER_REVIEW"

    APPROVED = "APPROVED"

    REJECTED = "REJECTED"

    ESCALATED = "ESCALATED"



class FindingStateMachine:


    transitions = {


        FindingStatus.DRAFT: [

            FindingStatus.UNDER_REVIEW

        ],



        FindingStatus.UNDER_REVIEW: [

            FindingStatus.APPROVED,

            FindingStatus.REJECTED,

            FindingStatus.ESCALATED,

        ],



        FindingStatus.APPROVED: [

            FindingStatus.ESCALATED

        ],



        FindingStatus.ESCALATED: [

            FindingStatus.APPROVED,

            FindingStatus.REJECTED

        ],



        FindingStatus.REJECTED: []

    }



    @classmethod
    def can_transition(
        cls,
        current,
        target
    ):

        try:

            current = FindingStatus(current)
            target = FindingStatus(target)

        except ValueError:

            return False


        return target in cls.transitions.get(
            current,
            []
        )