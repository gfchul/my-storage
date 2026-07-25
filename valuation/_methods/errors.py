class MissingInputError(Exception):
    """assumptions.yaml에 값(value)이 없는(null) 필수 입력이 있을 때 발생.

    소스 없는 값을 추정치로 대체하지 않고 계산을 거부하기 위한 용도.
    """

    def __init__(self, fields):
        self.fields = fields
        super().__init__("입력 누락: " + ", ".join(fields))
