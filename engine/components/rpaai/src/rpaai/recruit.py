from rpaai import InputType, JobWebsitesTypes, LLMModelTypes, RatingSystemTypes
from rpaai.api.llm import chat_prompt
from rpaai.utils.extract import FileExtractor
from rpaatomic import AtomicFormType, AtomicFormTypeMeta, DynamicsItem
from rpaatomic.atomic import atomicMg
from rpaframe.logger.logger import logger


class RecruitAI:
    keywords_boss = {
        "学历要求": ["不限", "本科及以上", "硕士及以上", "博士"],
        "院校要求": [
            "不限",
            "统招本科",
            "双一流院校",
            "211院校",
            "985院校",
            "留学生",
            "QS 100",
            "QS 500",
        ],
        "经验要求": ["不限", "在校/应届", "1-3年", "3-5年", "5-10年", "10年以上"],
        "年龄要求": [
            "不限",
            "20-25",
            "25-30",
            "30-35",
            "35-40",
            "40-45",
            "45-50",
            "50以上",
        ],
    }

    keywords_zhilian = {
        "学历要求": ["不限", "大专及以上", "本科及以上", "硕士及以上", "自定义"],
        "年龄要求": ["不限", "20-25", "25-30", "30-35", "35-40", "40以上", "自定义"],
        "经验要求": ["不限", "应届生", "1-3年", "3-5年", "5-10年", "自定义"],
        "院校要求": ["不限", "统招", "985", "211", "双一流", "海外院校"],
    }

    keywords_dict = {"boss": keywords_boss, "lieping": {}, "zhilian": keywords_zhilian}

    @atomicMg.atomic(
        "RecruitAI",
        inputList=[
            atomicMg.param(
                "job_description",
                formType=AtomicFormTypeMeta(type=AtomicFormType.INPUT_PYTHON_TEXTAREAMODAL_VARIABLE.value),
            ),
        ],
        outputList=[atomicMg.param("recruit_keywords", types="Str")],
    )
    def generate_keywords(
        self,
        job_name: str = "",
        job_description: str = "",
        job_website: JobWebsitesTypes = JobWebsitesTypes.BOSS,
    ):
        params = {
            "job_name": job_name,
            "job_description": job_description,
            "keywords_list": self.keywords_dict[job_website.value],
        }

        reply = chat_prompt(prompt_type="recruit_keywords", params=params)
        logger.info("RecruitAI generate_keywords: {}".format(reply))
        return reply

    @atomicMg.atomic(
        "RecruitAI",
        inputList=[
            atomicMg.param(
                "resume_content",
                dynamics=[
                    DynamicsItem(
                        key="$this.resume_content.show",
                        expression="return $this.resume_input_type.value == '{}'".format(InputType.TEXT.value),
                    )
                ],
            ),
            atomicMg.param(
                "resume_file_path",
                dynamics=[
                    DynamicsItem(
                        key="$this.resume_file_path.show",
                        expression="return $this.resume_input_type.value == '{}'".format(InputType.FILE.value),
                    )
                ],
                formType=AtomicFormTypeMeta(
                    type=AtomicFormType.INPUT_VARIABLE_PYTHON_FILE.value,
                    params={"filters": [], "file_type": "file"},
                ),
            ),
            atomicMg.param(
                "rating_dimensions",
                dynamics=[
                    DynamicsItem(
                        key="$this.rating_dimensions.show",
                        expression="return $this.rating_system.value == '{}'".format(RatingSystemTypes.CUSTOM.value),
                    )
                ],
            ),
        ],
        outputList=[atomicMg.param("recruit_rating", types="Str")],
    )
    def rating_resume(
        self,
        job_name,
        resume_input_type: InputType = InputType.TEXT,
        resume_file_path: str = "",
        resume_content: str = "",
        job_description: str = "",
        rating_system: RatingSystemTypes = RatingSystemTypes.DEFAULT,
        rating_dimensions: str = "",
    ):
        if resume_input_type == InputType.FILE:
            resume_content = FileExtractor(resume_file_path).extract_text()
        reply = ""
        if rating_system == RatingSystemTypes.DEFAULT:
            params = {
                "job_name": job_name,
                "job_description": job_description,
                "resume": resume_content,
            }
            reply = chat_prompt(prompt_type="recruit_rating_default", params=params)

        elif rating_system == RatingSystemTypes.CUSTOM:
            params = {
                "job_name": job_name,
                "rating_dimensions": rating_dimensions,
                "resume": resume_content,
            }
            reply = chat_prompt(prompt_type="recruit_rating_custom", params=params)

        logger.info("RecruitAI rating_resume: {}".format(reply))
        return reply
