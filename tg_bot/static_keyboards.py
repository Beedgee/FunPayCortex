# START OF FILE FunPayCortex-main/tg_bot/static_keyboards.py

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cortex import Cortex

from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B
from tg_bot import CBT, utils
from locales.localizer import Localizer

localizer = Localizer()
_ = localizer.translate


def CLEAR_STATE_BTN() -> K:
    return K().add(B(_("gl_cancel"), callback_data=CBT.CLEAR_STATE))


def REFRESH_BTN() -> K:
    return K().row(
        B("📊 " + _("stat_adv_stats_button"), callback_data=f"{CBT.STATS_MENU}:main"),
        B(_("gl_refresh"), callback_data=CBT.UPDATE_PROFILE)
    )

def ADV_PROFILE_STATS_BTN(account_name: str) -> K:
    return K().row(
        B(_("gl_back"), callback_data=f"{CBT.STATS_MENU}:main"),
        B(_("gl_configure"), callback_data=f"{CBT.STATS_CONFIG_MENU}:main"),
        B(_("gl_refresh"), callback_data=CBT.ADV_PROFILE_STATS)
    )


def SETTINGS_SECTIONS(cortex_instance: "Cortex", user_id: int) -> K:
    user_role = utils.get_user_role(cortex_instance.telegram.authorized_users, user_id)
    kb = K() \
        .add(B(_("mm_accounts"), callback_data=f"{CBT.ACCOUNTS_LIST}:0")) \
        .add(B(_("mm_language"), callback_data=f"{CBT.CATEGORY}:lang")) \
        .add(B(_("mm_autoresponse"), callback_data=f"{CBT.CATEGORY}:ar")) \
        .add(B(_("mm_autodelivery"), callback_data=f"{CBT.CATEGORY}:ad")) \
        .add(B(_("mm_templates"), callback_data=f"{CBT.TMPLT_LIST}:0"))

    if user_role == "admin":
        kb.add(B(_("mm_global"), callback_data=f"{CBT.CATEGORY}:main")) \
          .add(B(_("mm_plugins"), callback_data=f"{CBT.PLUGINS_LIST}:0"))

    kb.add(B(_("mm_notifications"), callback_data=f"{CBT.CATEGORY}:tg")) \
      .add(B(_("gl_next"), callback_data=CBT.MAIN2)) \
      .add(B("❌ " + _("gl_close"), callback_data=CBT.CLOSE_MENU))
    return kb


def SETTINGS_SECTIONS_2(cortex_instance: "Cortex", user_id: int) -> K:
    user_role = utils.get_user_role(cortex_instance.telegram.authorized_users, user_id)
    kb = K() \
        .add(B(_("mm_greetings"), callback_data=f"{CBT.CATEGORY}:gr")) \
        .add(B(_("mm_order_confirm"), callback_data=f"{CBT.CATEGORY}:oc")) \
        .add(B(_("mm_review_reply"), callback_data=f"{CBT.CATEGORY}:rr")) \
        .add(B(_("mm_new_msg_view"), callback_data=f"{CBT.CATEGORY}:mv"))

    if user_role == "admin" or cortex_instance.MAIN_CFG["ManagerPermissions"].getboolean("can_control_orders", fallback=False):
        kb.add(B(_("mm_order_control"), callback_data=f"{CBT.CATEGORY}:orc"))

    if user_role == "admin":
        kb.add(B(_("mm_blacklist"), callback_data=f"{CBT.CATEGORY}:bl")) \
          .add(B(_("mm_configs"), callback_data=CBT.CONFIG_LOADER)) \
          .add(B(_("mm_authorized_users"), callback_data=f"{CBT.AUTHORIZED_USERS}:0")) \
          .add(B(_("mm_proxy"), callback_data=f"{CBT.PROXY}:0"))

    kb.add(B(_("gl_back"), callback_data=CBT.MAIN))
    return kb

def AR_SETTINGS() -> K:
    """
    Генерирует клавиатуру настроек автоответчика.
    """
    kb = K(row_width=2)
    buttons = [
        B(_("ar_edit_commands"), callback_data=f"{CBT.CMD_LIST}:0"),
        B(_("ar_add_command"), callback_data=CBT.ADD_CMD)
    ]
    kb.add(*buttons)
    kb.add(B(_("gl_back"), callback_data=CBT.MAIN))
    return kb

def AD_SETTINGS() -> K:
    """
    Генерирует клавиатуру настроек автовыдачи.
    """
    kb = K(row_width=2)
    buttons = [
        B(_("ad_edit_autodelivery"), callback_data=f"{CBT.AD_LOTS_LIST}:0"),
        B(_("ad_add_autodelivery"), callback_data=f"{CBT.AD_CHOOSE_CATEGORY_LIST}:0"),
        B(_("ad_edit_goods_file"), callback_data=f"{CBT.PRODUCTS_FILES_LIST}:0")
    ]
    kb.add(*buttons)
    kb.add(B(_("gl_back"), callback_data=CBT.MAIN))
    return kb

def CONFIGS_UPLOADER() -> K:
    """
    Генерирует клавиатуру загрузки / выгрузки конфигов.
    """
    kb = K(row_width=2)
    buttons = [
        B(_("cfg_download_main"), callback_data=f"{CBT.DOWNLOAD_CFG}:main"),
        B(_("cfg_upload_main"), callback_data="upload_main_config"),
        B(_("cfg_download_ar"), callback_data=f"{CBT.DOWNLOAD_CFG}:autoResponse"),
        B(_("cfg_upload_ar"), callback_data="upload_auto_response_config"),
        B(_("cfg_download_ad"), callback_data=f"{CBT.DOWNLOAD_CFG}:autoDelivery"),
        B(_("cfg_upload_ad"), callback_data="upload_auto_delivery_config")
    ]
    kb.add(*buttons)
    kb.add(B(_("gl_back"), callback_data=CBT.MAIN2))
    return kb

# END OF FILE FunPayCortex-main/tg_bot/static_keyboards.py