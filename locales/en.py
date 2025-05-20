# START OF FILE FunPayCortex/locales/en.py

# Global
gl_next = "Next ▶️"
gl_back = "Back ◀️"
gl_yes = "Yes ✅"
gl_yep = "Yep ✅"
gl_no = "No ❌"
gl_cancel = "Cancel 🚫"
gl_error = "Error ⚠️"
gl_try_again = "Try again"
gl_error_try_again = f"{gl_error}. {gl_try_again}."
gl_refresh = "Refresh 🔄"
gl_delete = "Delete 🗑️"
gl_edit = "Edit ✏️"
gl_configure = "Configure ⚙️"
gl_pcs = "pcs."
gl_last_update = "Updated"
gl_refresh_and_try_again = "Refresh the list and try again."

# - Main Menu
mm_language = "🌍 Language"
mm_global = "🔧 General Settings"
mm_notifications = "🔔 Notifications"
mm_autoresponse = "🤖 Auto-Responder"
mm_autodelivery = "📦 Auto-Delivery"
mm_blacklist = "🚫 Blacklist"
mm_templates = "📝 Response Templates"
mm_greetings = "👋 Greetings"
mm_order_confirm = "👍 Order Confirmation Reply"
mm_review_reply = "⭐ Review Reply"
mm_new_msg_view = "💬 Notification View"
mm_plugins = "🧩 Plugins"
mm_configs = "🔩 Configurations"
mm_authorized_users = "👤 Users"
mm_proxy = "🌐 Proxy"

# Global Switches
gs_autoraise = "{} Auto-boost listings"
gs_autoresponse = "{} Auto-Responder"
gs_autodelivery = "{} Auto-Delivery"
gs_nultidelivery = "{} Multi-Delivery" # Assuming "nultidelivery" is a typo for "multidelivery"
gs_autorestore = "{} Restore listings"
gs_autodisable = "{} Deactivate listings"
gs_old_msg_mode = "{} Legacy message mode"
gs_keep_sent_messages_unread = "{} Don't mark as read when sending"

# Notification Settings
ns_new_msg = "{} New message"
ns_cmd = "{} Command received"
ns_new_order = "{} New order"
ns_order_confirmed = "{} Order confirmed"
ns_lot_activate = "{} Listing restored"
ns_lot_deactivate = "{} Listing deactivated"
ns_delivery = "{} Item delivered"
ns_raise = "{} Listings boosted"
ns_new_review = "{} New review"
ns_bot_start = "{} Bot started"
ns_other = "{} Other (plugins)"

# Auto-Responder Settings
ar_edit_commands = "✏️ Edit Commands"
ar_add_command = "➕ New Command"
ar_to_ar = "🤖 To Auto-Responder Settings"
ar_to_mm = "Menu 🏠"
ar_edit_response = "✏️ Edit Response Text"
ar_edit_notification = "✏️ Edit Notification Text"
ar_notification = "{} Notification in Telegram"
ar_add_more = "➕ Add More"
ar_add_another = "➕ Add Another"
ar_no_valid_commands_entered = "No valid commands entered."
ar_default_response_text = "The response for this command has not been configured yet. Please edit it."
ar_default_notification_text = "User $username entered command: $message_text"
ar_command_deleted_successfully = "Command/set '{command_name}' successfully deleted."

# Auto-Delivery Settings
ad_edit_autodelivery = "🗳️ Edit Auto-Delivery"
ad_add_autodelivery = "➕ Link Auto-Delivery"
ad_add_another_ad = "➕ Link Another"
ad_add_more_ad = "➕ Link More"
ad_edit_goods_file = "📋 Product Files"
ad_upload_goods_file = "📤 Upload File"
ad_create_goods_file = "➕ Create File"
ad_to_ad = "📦 To Auto-Delivery Settings"
never_updated = "never"
ad_default_response_text_new_lot = "Thank you for your purchase, $username!\nHere is your item:\n$product"

# - Edit Auto-Delivery
ea_edit_delivery_text = "✏️ Edit Delivery Text"
ea_link_goods_file = "🔗 Link Product File"
ea_delivery = "{} Auto-Delivery"
ea_multidelivery = "{} Multi-Delivery"
ea_restore = "{} Restore"
ea_deactivate = "{} Deactivate"
ea_test = "🔑 Test Key"
ea_more_test = "🔑 More Keys"
ea_link_another_gf = "🔗 Another File"

# - Add Auto-Delivery
fl_manual = "✍️ Enter Manually"

# - Product Files
gf_add_goods = "➕ Add Products"
gf_download = "📥 Download"
gf_create_another = "➕ Create Another"
gf_create_more = "➕ Create More"
gf_add_more = "➕ Add More"
gf_try_add_again = "➕ Try Again"
lot_info_header = "Listing Information"
text_not_set = "(text not set)"
gf_infinity = "infinity"
gf_count_error = "count error"
gf_file_not_found_short = "not found"
gf_not_linked = "not linked"
gf_file_created_now = "created"
gf_file_creation_error_short = "creation error"
no_lots_using_file = "No listings are using this file."
gf_no_products_to_add = "No products were entered to add."
gf_deleted_successfully = "File '{file_name}' successfully deleted."
gf_already_deleted = "File '{file_name}' was already deleted."


# Blacklist Settings
bl_autodelivery = "{} Do not deliver product"
bl_autoresponse = "{} Do not respond to commands"
bl_new_msg_notifications = "{} No notifications for new messages"
bl_new_order_notifications = "{} No notifications for new orders"
bl_command_notifications = "{} No notifications for commands"

# Response Templates
tmplt_add = "➕ New Template"
tmplt_add_more = "➕ More Templates"
tmplt_add_another = "➕ Another Template"
tmplt_editing_header = "📝 Editing Template"
tmplt_err_empty_text = "❌ Template text cannot be empty. Please enter text."
tmplt_deleted_successfully = "✅ Template '{template_text}' successfully deleted."

# Greeting Settings
gr_greetings = "{} Greet new users"
gr_ignore_sys_msgs = "{} Ignore system messages"
gr_edit_message = "✏️ Edit Greeting Text"
gr_edit_cooldown = "⏱️ Cooldown: {} days"

# Order Confirmation Reply Settings
oc_watermark = "{} Watermark"
oc_send_reply = "{} Send reply"
oc_edit_message = "✏️ Edit Reply Text"

# New Message Notification View Settings
mv_incl_my_msg = "{} My messages"
mv_incl_fp_msg = "{} FunPay messages"
mv_incl_bot_msg = "{} Bot messages"
mv_only_my_msg = "{} Only mine"
mv_only_fp_msg = "{} Only from FunPay"
mv_only_bot_msg = "{} Only from bot"
mv_show_image_name = "{} Image names"

# Plugins
pl_add = "➕ Add Plugin"
pl_activate = "🚀 Activate"
pl_deactivate = "💤 Deactivate"
pl_commands = "⌨️ Commands"
pl_settings = "⚙️ Settings"
pl_status_active = "Status: Active 🚀"
pl_status_inactive = "Status: Inactive 💤"
pl_no_commands = "This plugin has no registered commands."
pl_delete_handler_failed = "⚠️ Error executing delete handler for plugin '{plugin_name}'. Plugin removed from list, but its data or files might remain. Check logs."
pl_deleted_successfully = "✅ Plugin '{plugin_name}' successfully deleted. Restart FPCortex for changes to take effect."
pl_file_delete_error = "⚠️ Failed to delete plugin file '{plugin_path}'. Check permissions and logs."
pl_safe_source = "Source of safe plugins"
pl_channel_button = "FunPay Cortex Channel"


# Configs
cfg_download_main = "📥 Main Config"
cfg_download_ar = "📥 Auto-Responder Config"
cfg_download_ad = "📥 Auto-Delivery Config"
cfg_upload_main = "📤 Main Config"
cfg_upload_ar = "📤 Auto-Responder Config"
cfg_upload_ad = "📤 Auto-Delivery Config"

# Authorized Users
tg_block_login = "{} Block login by password"

# Proxy
prx_proxy_add = "➕ Add Proxy"
proxy_status_enabled = "Enabled"
proxy_status_disabled = "Disabled"
proxy_check_status_enabled = "Enabled"
proxy_check_status_disabled = "Disabled"
proxy_not_used_currently = "not currently used"
proxy_not_selected = "not selected"
proxy_check_interval_info = "Auto-check interval: {interval} min."
proxy_global_status_header = "Global Proxy Module Status"
proxy_module_status_label = "Module state:"
proxy_health_check_label = "Auto-proxy check:"
proxy_current_in_use_label = "Current proxy in use:"
proxy_select_error_not_found = "⚠️ Error: this proxy no longer exists in the list."
proxy_select_error_invalid_format = "⚠️ Error: the selected proxy has an invalid format."
proxy_selected_and_applied = "✅ Proxy {proxy_str} selected and applied."
proxy_selected_not_applied = "ℹ️ Proxy {proxy_str} selected. Enable the proxy module in settings for it to be used."
proxy_deleted_successfully = "✅ Proxy {proxy_str} successfully removed from the list."
proxy_delete_error_not_found = "⚠️ Error: proxy for deletion not found in the list."

# Announcements
an_an = "{} Announcements"
an_ad = "{} Advertisements"

# New Order
ord_refund = "💸 Refund"
ord_open = "🔗 Order Page"
ord_answer = "✉️ Reply"
ord_templates = "📝 Templates"

# New Message
msg_reply = "✉️ Reply"
msg_reply2 = "✉️ Reply Again"
msg_templates = "📝 Templates"
msg_more = "🔎 More Details"

# Message Texts
access_denied = """Hello, <b><i>{}</i></b>! 👋

Unfortunately, you do not have access. ⛔

🔑 Enter the <u><b>secret password</b></u> (specified during initial setup) to log in.

✨ <b>FunPay Cortex</b> - your best assistant on FunPay!
📢 Learn more and join our community on the channel: <a href="https://t.me/FunPayCortex"><b>FunPay Cortex Channel</b></a>"""
access_granted = "Access granted! 🔓\n\n" \
                 "📢 Note: notifications to <b><u>this chat</u></b> are not yet active.\n\n" \
                 "🔔 You can configure them in the menu.\n\n" \
                 "⚙️ Open <i>FPCortex</i> settings menu: /menu"
access_granted_notification = "<b>🚨 ATTENTION! 🚨\n\n\n</b>" * 3 + "\n\n\n🔐 User \"<a href=\"tg://user?id={1}\">{0}</a>\" " \
                                                                 "<b>(ID: {1}) has gained access to the Telegram control panel! 🔓</b>"
param_disabled = "❌ This setting is globally disabled and cannot be changed for this listing.\n\n" \
                 "🌍 Global settings are available here: " \
                 "/menu -> 🔧 General Settings."
old_mode_help = """<b>New message retrieval mode</b> 🚀
✅ <i>FPCortex</i> sees the entire chat history and all details of new messages.
✅ <i>FPCortex</i> can see images and forward them to <i>Telegram</i>.
✅ <i>FPCortex</i> accurately identifies the author: you, the interlocutor, or arbitration.
❌ The chat becomes "read" (does not glow orange) because <i>FPCortex</i> reads the entire history.

<b>Legacy message retrieval mode</b> 🐢
✅ Chats unread by you remain orange.
✅ Works slightly faster.
❌ <i>FPCortex</i> only sees the last message. If several messages arrive in a row – it will only see the last one.
❌ <i>FPCortex</i> does not see images and cannot forward them.
❌ <i>FPCortex</i> does not always accurately identify the author. If the chat is unread – the message is from the interlocutor, otherwise – from you. This logic can fail. Arbitration will also not be identified.

💡 If you press the <code>More Details</code> button in a notification, <i>FPCortex</i> will "read" the chat, show the last 15 messages (including pictures), and can accurately identify the author."""
bot_started = """✅ Telegram bot started!
You can <b><u>configure configs</u></b> and <b><u>use all features of the <i>Telegram</i> bot</u></b>.

⏳ <i>FPCortex</i> is <b><u>not yet initialized</u></b>, its functions are inactive.
When <i>FPCortex</i> starts, this message will change.

🕒 If initialization takes a long time, check the logs with the /logs command."""
fpc_init = """✅ <b><u>FPCortex initialized!</u></b>
ℹ️ <b><i>Version:</i></b> <code>{}</code>
👑 <b><i>Account:</i></b>  <code>{}</code> | <code>{}</code>
💰 <b><i>Balance:</i></b> <code>{}₽, {}$, {}€</code>
📊 <b><i>Active orders:</i></b>  <code>{}</code>

👨‍💻 <b><i>Author:</i></b> @beedge"""

create_test_ad_key = "Enter the listing name to test auto-delivery."
test_ad_key_created = """✅ A one-time key for delivering the listing '{<code>{}</code>}' has been created.
Send the command below in the chat with the buyer to deliver the product:
<code>!autodelivery {}</code>"""
about = """<b>🧠 FPCortex 🧠 v{}</b>
<i>Author:</i> @beedge"""
sys_info = """<b>📊 System Summary</b>

<b>⚙️ CPU:</b>
{}
    Used by <i>FPCortex</i>: <code>{}%</code>

<b>💾 RAM:</b>
    Total:  <code>{} MB</code>
    Used:  <code>{} MB</code>
    Free:  <code>{} MB</code>
    Used by bot:  <code>{} MB</code>

<b>⏱️ Other:</b>
    Uptime:  <code>{}</code>
    Chat ID:  <code>{}</code>"""
act_blacklist = """Enter the nickname of the user to add to the blacklist."""
already_blacklisted = "❌ User <code>{}</code> is already on the blacklist."
user_blacklisted = "✅ User <code>{}</code> added to the blacklist."
act_unban = "Enter the nickname of the user to remove from the blacklist."
not_blacklisted = "❌ User <code>{}</code> is not on the blacklist."
user_unbanned = "✅ User <code>{}</code> removed from the blacklist."
blacklist_empty = "🚫 The blacklist is empty."
act_proxy = "Enter proxy in the format <u>login:password@ip:port</u> or <u>ip:port</u>."
proxy_already_exists = "❌ Proxy <code>{}</code> already added."
proxy_added = "✅ Proxy <u>{}</u> successfully added."
proxy_format = "❌ Incorrect proxy format. Required: <u>login:password@ip:port</u> or <u>ip:port</u>."
proxy_adding_error = "⚠️ Error adding proxy."
proxy_undeletable = "❌ This proxy is in use and cannot be deleted."
act_edit_watermark = "Enter the new watermark text. Examples:\n{}\n<code>𝑭𝒖𝒏𝑷𝒂𝒚 𝑪𝒐𝒓𝒕𝒆𝒙</code>\n" \
                     "<code>FPCortex</code>\n<code>[FunPay / Cortex]</code>\n<code>𝑭𝑷𝑪𝒙</code>\n" \
                     "<code>FPCx</code>\n<code>🤖</code>\n<code>🧠</code>\n\n" \
                     "Examples can be copied and edited.\nNote that on FunPay the emoji " \
                     "🧠 might look different.\n\nTo remove the watermark, send <code>-</code>."
v_edit_watermark_current = "Current"
watermark_changed = "✅ Watermark changed."
watermark_deleted = "✅ Watermark removed."
watermark_error = "⚠️ Invalid watermark."
logfile_not_found = "❌ Log file not found."
logfile_sending = "Sending log file (this may take some time)... ⏳"
logfile_error = "⚠️ Failed to send log file."
logfile_deleted = "🗑️ Deleted {} log file(s)."
update_no_tags = "❌ Failed to get version list from GitHub. Try again later."
update_lasted = "✅ You have the latest version of FPCortex {} installed."
update_get_error = "❌ Failed to get new version information from GitHub. Try again later."
update_available = "✨ <b>A new version of FPCortex is available!</b> ✨\n\n{}"
update_update = "To update, enter the command /update"
update_backup = "✅ Backup created (configs, storage, plugins): <code>backup.zip</code>.\n\n" \
                "🔒 <b>IMPORTANT:</b> DO NOT SEND this archive to ANYONE. It contains all bot data and settings (including golden_key and products)."
update_backup_error = "⚠️ Failed to create backup."
update_backup_not_found = "❌ Backup not found."
update_downloaded = "✅ Update {} downloaded. Skipped {} items (if these were old releases). Installing..."
update_download_error = "⚠️ Error downloading update archive."
update_done = "✅ Update installed! Restart <i>FPCortex</i> with the /restart command."
update_done_exe = "✅ Update installed! The new <code>FPCortex.exe</code> is in the <code>update</code> folder. " \
                  "Turn off <i>FPCortex</i>, replace the old <code>FPCortex.exe</code> with the new one " \
                  "and run <code>Start.bat</code>."
update_install_error = "⚠️ Error installing update."

restarting = "Restarting... 🚀"
power_off_0 = """<b>Are you sure you want to turn me off?</b> 🤔
You <b><u>won't be able to</u></b> turn me back on via <i>Telegram</i>!"""
power_off_1 = "One more time, just in case... <b><u>Are you absolutely sure about turning off?</u></b> 😟"
power_off_2 = """Just so you know:
you'll have to go to the server/computer and start me manually! 💻"""
power_off_3 = """I'm not insisting, but if you need to apply changes to the main config,
you can just restart me with the /restart command. 😉"""
power_off_4 = "Are you even reading my messages? 😉 Let's check: yes = no, no = yes. " \
              "I bet you're not even reading, and I'm writing important information here."
power_off_5 = "So, your final answer is... yes? 😏"
power_off_6 = "Alright, alright, shutting down... 💤"
power_off_cancelled = "Shutdown cancelled. Resuming work! 👍"
power_off_error = "❌ This button is no longer relevant. Call the shutdown menu again."
enter_msg_text = "Enter message text:"
msg_sent = "✅ Message sent to chat <a href=\"https://funpay.com/chat/?node={}\">{}</a>."
msg_sent_short = "✅ Message sent."
msg_sending_error = "⚠️ Failed to send message to chat <a href=\"https://funpay.com/chat/?node={}\">{}</a>."
msg_sending_error_short = "⚠️ Failed to send message."
send_img = "Send me an image 🖼️"
greeting_changed = "✅ Greeting text changed."
greeting_cooldown_changed = "✅ Greeting cooldown changed: {} days."
order_confirm_changed = "✅ Order confirmation reply text changed!"
review_reply_changed = "✅ Reply text for {}⭐ review changed!"
review_reply_empty = "⚠️ Reply for {}⭐ review not set."
review_reply_text = "Reply for {}⭐ review:\n<code>{}</code>"
get_chat_error = "⚠️ Failed to get chat data."
viewing = "Viewing"
you = "You"
support = "tech support"
photo = "Photo"
refund_attempt = "⚠️ Failed to refund order <code>#{}</code>. Attempts left: <code>{}</code>."
refund_error = "❌ Failed to refund order <code>#{}</code>."
refund_complete = "✅ Funds for order <code>#{}</code> refunded."
updating_profile = "Updating account statistics... 📊"
profile_updating_error = "⚠️ Failed to update statistics."
acc_balance_available = "available"
act_change_golden_key = "🔑 Enter your golden_key:"
cookie_changed = "✅ golden_key successfully changed{}.\n"
cookie_changed2 = "Restart the bot with /restart command to apply changes."
cookie_incorrect_format = "❌ Incorrect golden_key format. Try again."
cookie_error = "⚠️ Failed to authorize. Perhaps an incorrect golden_key was entered?"
ad_lot_not_found_err = "⚠️ Listing with index <code>{}</code> not found."
ad_already_ad_err = "⚠️ Listing <code>{}</code> already has auto-delivery configured."
ad_lot_already_exists = "⚠️ Auto-delivery is already linked to listing <code>{}</code>."
ad_lot_linked = "✅ Auto-delivery linked to listing <code>{}</code>."
ad_link_gf = "Enter the name of the product file.\nTo unlink the file, send <code>-</code>\n\n" \
             "If the file does not exist, it will be created automatically."
ad_gf_unlinked = "✅ Product file unlinked from listing <code>{}</code>."
ad_gf_linked = "✅ File <code>storage/products/{}</code> linked to listing <code>{}</code>."
ad_gf_created_and_linked = "✅ File <code>storage/products/{}</code> <b><u>created</u></b> and linked to listing <code>{}</code>."
ad_creating_gf = "⏳ Creating file <code>storage/products/{}</code>..."
ad_product_var_err = "⚠️ Listing <code>{}</code> has a product file linked, but the delivery text is missing the <code>$product</code> variable."
ad_product_var_err2 = "⚠️ Cannot link file: the delivery text is missing the <code>$product</code> variable."
ad_text_changed = "✅ Delivery text for listing <code>{}</code> changed to:\n<code>{}</code>"
ad_updating_lots_list = "Updating listing and category data... ⏳"
ad_lots_list_updating_err = "⚠️ Failed to update listing and category data."
gf_not_found_err = "⚠️ Product file with index <code>{}</code> not found."
copy_lot_name = "Send the exact name of the listing (as on FunPay)."
act_create_gf = "Enter a name for the new product file (e.g., 'steam_keys')."
gf_name_invalid = "🚫 Invalid file name.\n\n" \
                  "Only <b><u>English</u></b> " \
                  "letters, numbers, and symbols <code>_</code>, <code>-</code>, and <code>space</code> are allowed." # Removed "and Russian"
gf_already_exists_err = "⚠️ File <code>{}</code> already exists."
gf_creation_err = "⚠️ Error creating file <code>{}</code>."
gf_created = "✅ File <code>storage/products/{}</code> created."
gf_amount = "Products in file"
gf_uses = "Used in listings"
gf_send_new_goods = "Send products to add. Each product on a new line (<code>Shift+Enter</code>)."
gf_add_goods_err = "⚠️ Failed to add products to file."
gf_new_goods = "✅ Added <code>{}</code> product(s) to file <code>storage/products/{}</code>."
gf_empty_error = "📂 File storage/products/{} is empty."
gf_linked_err = "⚠️ File <code>storage/products/{}</code> is linked to one or more listings.\n" \
                "Unlink it from all listings first, then delete."
gf_deleting_err = "⚠️ Failed to delete file <code>storage/products/{}</code>."
ar_cmd_not_found_err = "⚠️ Command with index <code>{}</code> not found."
ar_subcmd_duplicate_err = "⚠️ Command <code>{}</code> is duplicated in the set."
ar_cmd_already_exists_err = "⚠️ Command <code>{}</code> already exists."
ar_enter_new_cmd = "Enter a new command (or several, separated by <code>|</code>)."
ar_cmd_added = "✅ New command <code>{}</code> added."
ar_response_text = "Response text"
ar_notification_text = "Notification text"
ar_response_text_changed = "✅ Response text for command <code>{}</code> changed to:\n<code>{}</code>"
ar_notification_text_changed = "✅ Notification text for command <code>{}</code> changed to:\n<code>{}</code>"
cfg_main = "Main config. 🔒 IMPORTANT: DO NOT SEND this file to ANYONE."
cfg_ar = "Auto-Responder config."
cfg_ad = "Auto-Delivery config."
cfg_not_found_err = "⚠️ Config {} not found."
cfg_empty_err = "📂 Config {} is empty."
tmplt_not_found_err = "⚠️ Template with index <code>{}</code> not found."
tmplt_already_exists_err = "⚠️ Such a template already exists."
tmplt_added = "✅ Template added."
tmplt_msg_sent = "✅ Message from template sent to chat <a href=\"https://funpay.com/chat/?node={}\">{}</a>:\n\n<code>{}</code>"
pl_not_found_err = "⚠️ Plugin with UUID <code>{}</code> not found."
pl_file_not_found_err = "⚠️ File <code>{}</code> not found.\nRestart <i>FPCortex</i> with /restart command."
pl_commands_list = "Commands for plugin <b><i>{}</i></b>:"
pl_author = "Author"
pl_new = "Send me the plugin file (.py).\n\n<b>☢️ WARNING!</b> Loading plugins from unverified sources can be dangerous."
au_user_settings = "Settings for user {}"
adv_fpc = "😎 FPCortex - your best assistant for FunPay!"
adv_description = """🧠 FPCortex v{} 🚀

🤖 Auto-Delivery of goods
📈 Auto-boost listings
💬 Smart Auto-Responder
♻️ Auto-restore listings
📦 Auto-deactivation (if goods run out)
🔝 Always online
📲 Telegram notifications
🕹️ Full control via Telegram
🧩 Plugin support
🌟 And much more!

👨‍💻 Author: @beedge"""

# - Menu Descriptions
desc_main = "Hello! Choose what to configure 👇"
desc_lang = "Choose interface language:"
desc_gs = "Here you can enable or disable the main functions of <i>FPCortex</i>."
desc_ns = """Configure notifications for this chat.
Each chat is configured separately!

ID of this chat: <code>{}</code>"""
desc_bl = "Set restrictions for users from the blacklist."
desc_ar = "Add commands for the auto-responder or edit existing ones."
desc_ar_list = "Choose a command or set of commands to edit:"
desc_ad = "Auto-delivery settings: linking to listings, managing product files, etc."
desc_ad_list = "List of listings with configured auto-delivery. Choose a listing to edit:"
desc_ad_fp_lot_list = "List of listings from your FunPay profile. Choose a listing to configure auto-delivery.\n" \
                      "If the desired listing is not present, press <code>🔄 Refresh</code>.\n\n" \
                      "Last scan: {}"
desc_gf = "Choose a product file to manage:"
desc_mv = "Configure how new message notifications will look."
desc_gr = "Configure greeting messages for new dialogues.\n\n<b>Current greeting text:</b>\n<code>{}</code>"
desc_oc = "Configure the message that will be sent when an order is confirmed.\n\n<b>Current message text:</b>\n<code>{}</code>"
desc_or = "Configure automatic responses to reviews."
desc_an = "Announcement notification settings."
desc_cfg = "Here you can download or upload configuration files."
desc_tmplt = "Manage quick response templates."
desc_pl = "Plugin information and settings.\n\n" \
          "⚠️ <b>IMPORTANT:</b> After activating, deactivating, adding, or deleting a plugin, " \
          "<b><u>you must restart the bot</u></b> with the /restart command!"
desc_au = "User authorization settings in the Telegram control panel."
desc_proxy = "Manage proxy servers for bot operation."
unknown_action = "Unknown action or button has expired."

# - Command Descriptions
cmd_menu = "open main menu"
cmd_language = "change interface language"
cmd_profile = "view account statistics"
cmd_golden_key = "change golden_key (access token)"
cmd_test_lot = "create test auto-delivery key"
cmd_upload_chat_img = "(chat) upload image to FunPay"
cmd_upload_offer_img = "(listing) upload image to FunPay"
cmd_upload_plugin = "upload new plugin"
cmd_ban = "add user to blacklist"
cmd_unban = "remove user from blacklist"
cmd_black_list = "show blacklist"
cmd_watermark = "change message watermark"
cmd_logs = "download current log file"
cmd_del_logs = "delete old log files"
cmd_about = "bot information"
cmd_check_updates = "check for updates"
cmd_update = "update bot"
cmd_sys = "system information and load"
cmd_create_backup = "create backup"
cmd_get_backup = "download backup"
cmd_restart = "restart FPCortex"
cmd_power_off = "turn off FPCortex"

# - Variable Descriptions
v_edit_greeting_text = "Enter greeting message text:"
v_edit_greeting_cooldown = "Enter cooldown for greeting (in days, e.g., 0.5 for 12 hours):"
v_edit_order_confirm_text = "Enter order confirmation reply text:"
v_edit_review_reply_text = "Enter reply text for {}⭐ review:"
v_edit_delivery_text = "Enter new text for auto-delivery of the product:"
v_edit_response_text = "Enter new response text for the command:"
v_edit_notification_text = "Enter new text for Telegram notification:"
V_new_template = "Enter text for the new response template:"
v_list = "Available variables:"
v_date = "<code>$date</code> - date (DD.MM.YYYY)"
v_date_text = "<code>$date_text</code> - date (January 1)"
v_full_date_text = "<code>$full_date_text</code> - date (January 1, 2001)"
v_time = "<code>$time</code> - time (HH:MM)"
v_full_time = "<code>$full_time</code> - time (HH:MM:SS)"
v_photo = "<code>$photo=[PHOTO_ID]</code> - picture (ID via /upload_chat_img)"
v_sleep = "<code>$sleep=[SECONDS]</code> - delay before sending (e.g., $sleep=2)"
v_order_id = "<code>$order_id</code> - order ID (without #)"
v_order_link = "<code>$order_link</code> - link to order"
v_order_title = "<code>$order_title</code> - order title"
v_order_params = "<code>$order_params</code> - order parameters"
v_order_desc_and_params = "<code>$order_desc_and_params</code> - order title and/or parameters"
v_order_desc_or_params = "<code>$order_desc_or_params</code> - order title or parameters"
v_game = "<code>$game</code> - game name"
v_category = "<code>$category</code> - subcategory name"
v_category_fullname = "<code>$category_fullname</code> - full name (subcategory + game)"
v_product = "<code>$product</code> - product from file (if not linked, will not be replaced)"
v_chat_id = "<code>$chat_id</code> - chat ID"
v_chat_name = "<code>$chat_name</code> - chat name"
v_message_text = "<code>$message_text</code> - interlocutor's message text"
v_username = "<code>$username</code> - interlocutor's nickname"
v_cpu_core = "Core"

# Exception Texts
exc_param_not_found = "Parameter \"{}\" not found."
exc_param_cant_be_empty = "Value of parameter \"{}\" cannot be empty."
exc_param_value_invalid = "Invalid value for \"{}\". Allowed: {}. Current: \"{}\"."
exc_goods_file_not_found = "Product file \"{}\" not found."
exc_goods_file_is_empty = "File \"{}\" is empty."
exc_not_enough_items = "Not enough products in file \"{}\". Needed: {}, available: {}."
exc_no_product_var = "\"productsFileName\" specified, but parameter \"response\" is missing the $product variable."
exc_no_section = "Section is missing."
exc_section_duplicate = "Duplicate section detected."
exc_cmd_duplicate = "Command or sub-command \"{}\" already exists."
exc_cfg_parse_err = "Error in config {}, section [{}]: {}"
exc_plugin_field_not_found = "Failed to load plugin \"{}\": missing required field \"{}\"."

# Logs (Primarily for developers, static parts kept as-is or minimally translated for clarity)
log_tg_initialized = "$MAGENTATelegram bot initialized."
log_tg_started = "$CYANTelegram bot $YELLOW@{}$CYAN started."
log_tg_handler_error = "An error occurred while executing Telegram bot handler."
log_tg_update_error = "An error ({}) occurred while fetching Telegram updates (incorrect token entered?)."
log_tg_notification_error = "An error occurred while sending notification to chat $YELLOW{}$RESET."
log_access_attempt = "$MAGENTA@{} (ID: {})$RESET attempted to access CP. Holding them back as best I can!"
log_click_attempt = "$MAGENTA@{} (ID: {})$RESET is clicking CP buttons in chat $MAGENTA@{} (ID: {})$RESET. It won't work for them!"
log_access_granted = "$MAGENTA@{} (ID: {})$RESET gained access to CP."
log_new_ad_key = "$MAGENTA@{} (ID: {})$RESET created a delivery key for $YELLOW{}$RESET: $CYAN{}$RESET."
log_user_blacklisted = "$MAGENTA@{} (ID: {})$RESET added $YELLOW{}$RESET to blacklist."
log_user_unbanned = "$MAGENTA@{} (ID: {})$RESET removed $YELLOW{}$RESET from blacklist."
log_watermark_changed = "$MAGENTA@{} (ID: {})$RESET changed message watermark to $YELLOW{}$RESET."
log_watermark_deleted = "$MAGENTA@{} (ID: {})$RESET deleted message watermark."
log_greeting_changed = "$MAGENTA@{} (ID: {})$RESET changed greeting text to $YELLOW{}$RESET."
log_greeting_cooldown_changed = "$MAGENTA@{} (ID: {})$RESET changed greeting message cooldown to $YELLOW{}$RESET days."
log_order_confirm_changed = "$MAGENTA@{} (ID: {})$RESET changed order confirmation reply text to $YELLOW{}$RESET."
log_review_reply_changed = "$MAGENTA@{} (ID: {})$RESET changed reply text for {} star review to $YELLOW{}$RESET."
log_param_changed = "$MAGENTA@{} (ID: {})$RESET changed parameter $CYAN{}$RESET of section $YELLOW[{}]$RESET to $YELLOW{}$RESET."
log_notification_switched = "$MAGENTA@{} (ID: {})$RESET switched $YELLOW{}$RESET notifications for chat $YELLOW{}$RESET to $CYAN{}$RESET."
log_ad_linked = "$MAGENTA@{} (ID: {})$RESET linked auto-delivery to listing $YELLOW{}$RESET."
log_ad_text_changed = "$MAGENTA@{} (ID: {})$RESET changed delivery text for listing $YELLOW{}$RESET to $YELLOW\"{}\"$RESET."
log_ad_deleted = "$MAGENTA@{} (ID: {})$RESET deleted auto-delivery for listing $YELLOW{}$RESET."
log_gf_created = "$MAGENTA@{} (ID: {})$RESET created product file $YELLOWstorage/products/{}$RESET."
log_gf_unlinked = "$MAGENTA@{} (ID: {})$RESET unlinked product file from listing $YELLOW{}$RESET."
log_gf_linked = "$MAGENTA@{} (ID: {})$RESET linked product file $YELLOWstorage/products/{}$RESET to listing $YELLOW{}$RESET."
log_gf_created_and_linked = "$MAGENTA@{} (ID: {})$RESET created and linked product file $YELLOWstorage/products/{}$RESET to listing $YELLOW{}$RESET."
log_gf_new_goods = "$MAGENTA@{} (ID: {})$RESET added $CYAN{}$RESET product(s) to file $YELLOWstorage/products/{}$RESET."
log_gf_downloaded = "$MAGENTA@{} (ID: {})$RESET requested product file $YELLOWstorage/products/{}$RESET."
log_gf_deleted = "$MAGENTA@{} (ID: {})$RESET deleted product file $YELLOWstorage/products/{}$RESET."
log_ar_added = "$MAGENTA@{} (ID: {})$RESET added new command $YELLOW{}$RESET."
log_ar_response_text_changed = "$MAGENTA@{} (ID: {})$RESET changed response text for command $YELLOW{}$RESET to $YELLOW\"{}\"$RESET."
log_ar_notification_text_changed = "$MAGENTA@{} (ID: {})$RESET changed notification text for command $YELLOW{}$RESET to $YELLOW\"{}\"$RESET."
log_ar_cmd_deleted = "$MAGENTA@{} (ID: {})$RESET deleted command $YELLOW{}$RESET."
log_cfg_downloaded = "$MAGENTA@{} (ID: {})$RESET requested config $YELLOW{}$RESET."
log_tmplt_added = "$MAGENTA@{} (ID: {})$RESET added response template $YELLOW\"{}\"$RESET."
log_tmplt_deleted = "$MAGENTA@{} (ID: {})$RESET deleted response template $YELLOW\"{}\"$RESET."
log_pl_activated = "$MAGENTA@{} (ID: {})$RESET activated plugin $YELLOW\"{}\"$RESET."
log_pl_deactivated = "$MAGENTA@{} (ID: {})$RESET deactivated plugin $YELLOW\"{}\"$RESET."
log_pl_deleted = "$MAGENTA@{} (ID: {})$RESET deleted plugin $YELLOW\"{}\"$RESET."
log_pl_delete_handler_err = "An error occurred while executing delete handler for plugin $YELLOW\"{}\"$RESET."

# Handler Logs
log_new_msg = "$MAGENTA┌──$RESET New message in conversation with user $YELLOW{} (CID: {}):"
log_sending_greetings = "User $YELLOW{} (CID: {})$RESET wrote for the first time! Sending greeting message..."
log_new_cmd = "Command $YELLOW{}$RESET received in chat with user $YELLOW{} (CID: {})$RESET."
ntfc_new_order = "💰 <b>New order:</b> <code>{}</code>\n\n<b><i>🙍‍♂️ Buyer:</i></b>  <code>{}</code>\n" \
                 "<b><i>💵 Amount:</i></b>  <code>{}</code>\n<b><i>📇 ID:</i></b> <code>#{}</code>\n\n<i>{}</i>"
ntfc_new_order_not_in_cfg = "ℹ️ Product will not be delivered as auto-delivery is not linked to the listing."
ntfc_new_order_ad_disabled = "ℹ️ Product will not be delivered as auto-delivery is disabled in global switches."
ntfc_new_order_ad_disabled_for_lot = "ℹ️ Product will not be delivered as auto-delivery is disabled for this listing."
ntfc_new_order_user_blocked = "ℹ️ Product will not be delivered as the user is blacklisted and auto-delivery blocking is enabled."
ntfc_new_order_will_be_delivered = "ℹ️ Product will be delivered shortly."
ntfc_new_review = "🔮 You received {} for order <code>{}</code>!\n\n💬<b>Review:</b>\n<code>{}</code>{}"
ntfc_review_reply_text = "\n\n🗨️<b>Reply:</b> \n<code>{}</code>"

# Cortex Logs
crd_proxy_detected = "Proxy detected."
crd_checking_proxy = "Performing proxy check..."
crd_proxy_err = "Failed to connect to proxy. Ensure data is entered correctly."
crd_proxy_success = "Proxy successfully checked! IP address: $YELLOW{}$RESET."
crd_acc_get_timeout_err = "Failed to load account data: timeout exceeded."
crd_acc_get_unexpected_err = "An unexpected error occurred while fetching account data."
crd_try_again_in_n_secs = "Retrying in {} second(s)..."
crd_getting_profile_data = "Fetching listing and category data..."
crd_profile_get_timeout_err = "Failed to load account listing data: timeout exceeded."
crd_profile_get_unexpected_err = "An unexpected error occurred while fetching listing and category data."
crd_profile_get_too_many_attempts_err = "An error occurred while fetching listing and category data: attempt limit ({}) exceeded."
crd_profile_updated = "Updated information about listings $YELLOW({})$RESET and categories $YELLOW({})$RESET of the profile."
crd_tg_profile_updated = "Updated information about listings $YELLOW({})$RESET and categories $YELLOW({})$RESET of the profile (TG CP)."
crd_raise_time_err = 'Failed to boost listings in category $CYAN\"{}\"$RESET. FunPay says: "{}". Next attempt in {}.'
crd_raise_unexpected_err = "An unexpected error occurred while trying to boost listings in category $CYAN\"{}\"$RESET. Pausing for 10 seconds..."
crd_raise_status_code_err = "Error {} while boosting listings in category $CYAN\"{}\"$RESET. Pausing for 1 min..."
crd_lots_raised = "All listings in category $CYAN\"{}\"$RESET boosted!"
crd_raise_wait_3600 = "Next attempt in {}."
crd_msg_send_err = "An error occurred while sending message to chat $YELLOW{}$RESET."
crd_msg_attempts_left = "Attempts left: $YELLOW{}$RESET."
crd_msg_no_more_attempts_err = "Failed to send message to chat $YELLOW{}$RESET: attempt limit exceeded."
crd_msg_sent = "Sent message to chat $YELLOW{}."
crd_session_timeout_err = "Failed to update session: timeout exceeded."
crd_session_unexpected_err = "An unexpected error occurred while updating session."
crd_session_no_more_attempts_err = "Failed to update session: attempt limit exceeded."
crd_session_updated = "Session updated."
crd_raise_loop_started = "$CYANAuto-boost listings loop started (this does not mean auto-boost is enabled)."
crd_raise_loop_not_started = "$CYANAuto-boost loop was not started as no listings were found on the account."
crd_session_loop_started = "$CYANSession update loop started."
crd_no_plugins_folder = "Plugins folder not found."
crd_no_plugins = "Plugins not found."
crd_plugin_load_err = "Failed to load plugin {}."
crd_invalid_uuid = "Failed to load plugin {}: invalid UUID."
crd_uuid_already_registered = "UUID {} ({}) already registered."
crd_handlers_registered = "Handlers from $YELLOW{}.py$RESET registered."
crd_handler_err = "An error occurred while executing handler."
crd_tg_au_err = "Failed to change message with user information: {}. Trying without link."

acc_balance_available = "available"
gf_infinity = "infinity"
gf_count_error = "count error"
gf_file_not_found_short = "not found"
gf_not_linked = "not linked"
gf_file_created_now = "created"
gf_file_creation_error_short = "creation error"
no_lots_using_file = "No listings are using this file."
gf_no_products_to_add = "No products were entered to add."
gf_deleted_successfully = "File '{file_name}' successfully deleted."
gf_already_deleted = "File '{file_name}' was already deleted."
ar_no_valid_commands_entered = "No valid commands entered."
ar_default_response_text = "The response for this command has not been configured yet. Please edit it."
ar_default_notification_text = "User $username entered command: $message_text"
ar_command_deleted_successfully = "Command/set '{command_name}' successfully deleted."
file_err_not_detected = "❌ File not found in message."
file_err_must_be_text = "❌ File must be text-based (e.g., .txt, .cfg, .py, .json, .ini, .log)."
file_err_wrong_format = "❌ Incorrect file format: <b><u>.{actual_ext}</u></b> (expected <b><u>.{expected_ext}</u></b>)."
file_err_too_large = "❌ File size must not exceed 20MB."
file_info_downloading = "⏬ Downloading file from Telegram servers..."
file_err_download_failed = "❌ An error occurred while downloading the file to the bot server."
file_info_checking_validity = "🤔 Checking file content..."
file_err_processing_generic = "⚠️ An error occurred while processing the file: <code>{error_message}</code>"
file_err_utf8_decode = "Error reading file (UTF-8). Ensure the file encoding is UTF-8 and line endings are LF."
file_info_main_cfg_loaded = "✅ Main config successfully loaded.\n\n⚠️ <b>Bot restart required (/restart)</b> for changes to take effect.\n\nAny changes to the main config via control panel switches before restarting will override loaded settings."
file_info_ar_cfg_applied = "✅ Auto-Responder config successfully loaded and applied."
file_info_ad_cfg_applied = "✅ Auto-Delivery config successfully loaded and applied."
plugin_uploaded_success = "✅ Plugin <code>{filename}</code> successfully uploaded.\n\n⚠️For the plugin to work, <b><u>restart FPCortex!</u></b> (/restart)"
image_upload_unsupported_format = "❌ Unsupported image format. Available: <code>.png</code>, <code>.jpg</code>, <code>.jpeg</code>, <code>.gif</code>."
image_upload_error_generic = "⚠️ Failed to upload image to FunPay. See log file (<code>logs/log.log</code>) for details."
image_upload_chat_success_info = "Use this ID in auto-delivery or auto-response texts with the <code>$photo</code> variable.\n\nExample: <code>$photo={image_id}</code>"
image_upload_offer_success_info = "Use this ID to add images to your listings on FunPay."
image_upload_success_header = "✅ Image successfully uploaded to FunPay server.\n\n<b>Image ID:</b> <code>{image_id}</code>\n\n"
products_file_provide_prompt = "📎 Send me the product file (.txt):"
products_file_upload_success = "✅ Product file <code>{filepath}</code> successfully uploaded. Products in file: <code>{count}</code>."
products_file_count_error = "⚠️ Error counting products in uploaded file."
main_config_provide_prompt = "⚙️ Send me the main config file (<code>_main.cfg</code>):"
ar_config_provide_prompt = "🤖 Send me the auto-responder config file (<code>auto_response.cfg</code>):"
ad_config_provide_prompt = "📦 Send me the auto-delivery config file (<code>auto_delivery.cfg</code>):"
pl_status_active = "Status: Active 🚀"
pl_status_inactive = "Status: Inactive 💤"
pl_no_commands = "This plugin has no registered commands."
pl_delete_handler_failed = "⚠️ Error executing delete handler for plugin '{plugin_name}'. Plugin removed from list, but its data or files might remain. Check logs."
pl_deleted_successfully = "✅ Plugin '{plugin_name}' successfully deleted. Restart FPCortex for changes to take effect."
pl_file_delete_error = "⚠️ Failed to delete plugin file '{plugin_path}'. Check permissions and logs."
proxy_status_enabled = "Enabled"
proxy_status_disabled = "Disabled"
proxy_check_status_enabled = "Enabled"
proxy_check_status_disabled = "Disabled"
proxy_not_used_currently = "not currently used"
proxy_not_selected = "not selected"
proxy_check_interval_info = "Auto-check interval: {interval} min."
proxy_global_status_header = "Global Proxy Module Status"
proxy_module_status_label = "Module state:"
proxy_health_check_label = "Auto-proxy check:"
proxy_current_in_use_label = "Current proxy in use:"
proxy_select_error_not_found = "⚠️ Error: this proxy no longer exists in the list."
proxy_select_error_invalid_format = "⚠️ Error: the selected proxy has an invalid format."
proxy_selected_and_applied = "✅ Proxy {proxy_str} selected and applied."
proxy_selected_not_applied = "ℹ️ Proxy {proxy_str} selected. Enable the proxy module in settings for it to be used."
proxy_deleted_successfully = "✅ Proxy {proxy_str} successfully removed from the list."
proxy_delete_error_not_found = "⚠️ Error: proxy for deletion not found in the list."
tmplt_editing_header = "📝 Editing Template"
tmplt_err_empty_text = "❌ Template text cannot be empty. Please enter text."
tmplt_deleted_successfully = "✅ Template '{template_text}' successfully deleted."
no_messages_to_display = "No messages to display"
# END OF FILE FunPayCortex/locales/en.py