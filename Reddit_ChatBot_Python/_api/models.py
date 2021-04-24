from dataclasses import dataclass
from typing import Dict, Optional, List
from enum import Enum
from dacite import from_dict, Config


class CustomType(Enum):
    group = 'group'
    direct = 'direct'


class MemberState(Enum):
    joined = 'joined'
    invited = 'invited'


@dataclass(frozen=True)
class _Channel:
    name: str
    member_count: int
    custom_type: CustomType
    channel_url: str
    created_at: int
    # cover_url: str
    max_length_message: int
    data: str


@dataclass(frozen=True)
class _MentionedUser:
    nickname: str
    # metadata: dict
    # require_auth_for_profile_image: bool
    # profile_url: str
    user_id: str


@dataclass(frozen=True)
class _User:
    require_auth_for_profile_image: bool
    is_active: Optional[bool]
    is_blocked_by_me: Optional[bool]
    role: str
    user_id: str
    nickname: str
    # profile_url: str
    # metadata: dict


@dataclass(frozen=True)
class _CreatedBy:
    # require_auth_for_profile_image: bool
    nickname: str
    user_id: str
    # profile_url: str


@dataclass(frozen=True)
class _Member:
    is_blocking_me: Optional[bool]
    user_id: str
    is_muted: bool
    friend_name: Optional[str]
    is_active: Optional[bool]
    is_blocked_by_me: Optional[bool]
    state: str
    # friend_discovery_key: null
    role: str
    is_online: Optional[bool]
    require_auth_for_profile_image: bool
    # last_seen_at: int
    nickname: str
    # profile_url:str
    # metadata: dict


@dataclass(frozen=True)
class Message:
    # message_survival_seconds: int
    # custom_type: str
    mentioned_users: List[_MentionedUser]
    # translations: dict
    updated_at: int
    is_op_msg: bool
    is_removed: bool
    user: _User
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

    @classmethod
    def from_dict(cls, d):
        return from_dict(data=d, data_class=cls)


@dataclass(frozen=True)
class Channel:
    invited_at: int
    custom_type: CustomType
    # is_ephemeral: bool
    read_receipt: Dict[str, int]
    member_state: MemberState
    freeze: bool
    created_by: Optional[_CreatedBy]
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
    members: List[_Member]
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
    inviter: _CreatedBy
    count_preference: str

    @classmethod
    def from_dict(cls, d):
        return from_dict(data=d, data_class=cls, config=Config(cast=[CustomType, MemberState]))
