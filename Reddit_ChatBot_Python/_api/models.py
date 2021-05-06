from typing import Dict, Optional, List, Union
from enum import Enum
from pydantic import BaseModel, Json


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
    data: Union[Json, str]

    class Config:
        allow_mutation = False


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

    class Config:
        allow_mutation = False


class Members(BaseModel):
    members: List[User]
    next: str

    class Config:
        allow_mutation = False

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class Message(BaseModel):
    # message_survival_seconds: int
    # custom_type: str
    mentioned_users: List[User]
    # translations: dict
    updated_at: int
    is_op_msg: bool
    is_removed: bool
    user: User
    # file: dict
    message: str
    data: str
    # message_retention_hour: int
    # silent: bool
    type: str
    created_at: int
    req_id: Optional[str]
    mention_type: str
    channel_url: str
    message_id: int

    class Config:
        allow_mutation = False

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


class Channel(BaseModel):
    invited_at: int
    custom_type: CustomType
    # is_ephemeral: bool
    read_receipt: Dict[str, int]
    member_state: MemberState
    freeze: bool
    created_by: Optional[User]
    is_hidden: bool
    # disappearing_message: dict
    is_push_enabled: bool
    joined_ts: Optional[int]
    is_created: Optional[bool]
    member_count: int
    # my_role: str
    # is_broadcast: bool
    last_message: Optional[Message]
    user_last_read: int
    unread_mention_count: int
    # sms_fallback: dict
    # is_discoverable: bool
    # ignore_profanity_filter: bool
    channel_url: str
    # operators: list
    channel: _Channel
    # message_survival_seconds: int
    unread_message_count: int
    # is_distinct: bool
    # is_muted: bool
    # hidden_state: str
    cover_url: str
    members: List[User]
    is_public: bool
    # data: str
    # ts_message_offset: int
    joined_member_count: int
    is_super: bool
    name: str
    created_at: int
    # is_access_code_required: bool
    # push_trigger_option: str
    max_length_message: int
    inviter: User
    count_preference: str

    class Config:
        allow_mutation = False

    @classmethod
    def from_dict(cls, d):
        return cls(**d)
