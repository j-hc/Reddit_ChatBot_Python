from typing import Dict, Optional, List
from enum import Enum
from pydantic import BaseModel as PydanticBaseModel, BaseConfig as PydanticBaseConfig


class BaseConfig(PydanticBaseConfig):
    allow_mutation = False
    frozen = True


class BaseModel(PydanticBaseModel):
    Config = BaseConfig

    @classmethod
    def construct(cls, **values):
        m = cls.__new__(cls)
        fields_values = {}

        config = cls.__config__

        for name, field in cls.__fields__.items():
            key = field.alias
            if key not in values and config.allow_population_by_field_name:
                key = name
            if key in values:
                if values[key] is None and not field.required:
                    fields_values[name] = field.get_default()
                else:
                    if issubclass(field.type_, BaseModel):
                        if field.shape == 2:
                            fields_values[name] = [
                                field.type_.construct(**e)
                                for e in values[key]
                            ]
                        else:
                            fields_values[name] = field.outer_type_.construct(**values[key])
                    else:
                        fields_values[name] = values[key]
            elif not field.required:
                fields_values[name] = field.get_default()

        object.__setattr__(m, '__dict__', fields_values)
        _fields_set = set(values.keys())
        object.__setattr__(m, '__fields_set__', _fields_set)
        m._init_private_attributes()
        return m


class CustomType(str, Enum):
    group = 'group'
    direct = 'direct'


class MemberState(str, Enum):
    joined = 'joined'
    invited = 'invited'


class _Channel(BaseModel):
    name: str
    member_count: int
    custom_type: CustomType
    channel_url: str
    created_at: int
    # cover_url: str
    max_length_message: int
    data: str


class User(BaseModel):
    is_blocking_me: Optional[bool]
    user_id: Optional[str]
    is_muted: Optional[bool]
    friend_name: Optional[str]
    joined_ts: Optional[int]
    is_active: Optional[bool]
    read_ts: Optional[int]
    is_blocked_by_me: Optional[bool]
    state: Optional[str]
    # friend_discovery_key: null
    role: Optional[str]
    is_online: Optional[bool]
    require_auth_for_profile_image: Optional[bool]
    # last_seen_at: int
    nickname: Optional[str]
    # profile_url:str
    # metadata: dict


class Members(BaseModel):
    members: List[User]
    next: str


class BannedUser(BaseModel):
    description: str
    start_at: int
    user: User
    end_at: int


class BannedUsers(BaseModel):
    banned_list: List[BannedUser]
    next: str


class Message(BaseModel):
    # message_survival_seconds: int
    # custom_type: str
    mentioned_users: List[User]
    # translations: dict
    updated_at: Optional[int]
    is_op_msg: Optional[bool]
    is_removed: Optional[bool]
    user: Optional[User]
    # file: dict
    message: str
    data: str
    # message_retention_hour: int
    # silent: bool
    type: Optional[str]
    created_at: Optional[int]
    req_id: Optional[str]
    mention_type: Optional[str]
    channel_url: str
    message_id: Optional[int]


class Channel(BaseModel):
    invited_at: Optional[int]
    custom_type: CustomType
    # is_ephemeral: bool
    read_receipt: Dict[str, int]
    member_state: MemberState
    freeze: Optional[bool]
    created_by: Optional[User]
    is_hidden: Optional[bool]
    # disappearing_message: dict
    is_push_enabled: Optional[bool]
    joined_ts: Optional[int]
    is_created: Optional[bool]
    member_count: Optional[int]
    # my_role: str
    # is_broadcast: bool
    last_message: Optional[Message]
    user_last_read: Optional[int]
    unread_mention_count: Optional[int]
    # sms_fallback: dict
    # is_discoverable: bool
    # ignore_profanity_filter: bool
    channel_url: str
    operators: Optional[List[User]]
    channel: _Channel
    # message_survival_seconds: int
    unread_message_count: Optional[int]
    # is_distinct: bool
    # is_muted: bool
    # hidden_state: str
    cover_url: Optional[str]
    members: List[User]
    is_public: Optional[bool]
    # data: Union[Json, str]
    # ts_message_offset: int
    joined_member_count: Optional[int]
    is_super: Optional[bool]
    name: Optional[str]
    created_at: Optional[int]
    # is_access_code_required: bool
    # push_trigger_option: str
    max_length_message: Optional[int]
    inviter: Optional[User]
    count_preference: Optional[str]
