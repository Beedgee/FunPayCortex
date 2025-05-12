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
gl_refresh_and_try_again = "Refresh the list and try again." # For auto_delivery_cp.py

# - Main Menu
mm_language = "🌍 Language"
mm_global = "🔧 General Settings"
mm_notifications = "🔔 Notifications"
mm_autoresponse = "🤖 Auto-Responder"
mm_autodelivery = "📦 Auto-Delivery"
mm_blacklist = "🚫 Blacklist"
mm_templates = "📝 Response Templates"
mm_greetings = "👋 Greetings"
mm_order_confirm = "👍 Confirmation Response"
mm_review_reply = "⭐ Review Reply"
mm_new_msg_view = "💬 Notification View"
mm_plugins = "🧩 Plugins"
mm_configs = "🔩 Configurations"
mm_authorized_users = "👤 Users"
mm_proxy = "🌐 Proxy"

# Global Switches
gs_autoraise = "{} Auto-boost Lots"
gs_autoresponse = "{} Auto-Responder"
gs_autodelivery = "{} Auto-Delivery"
gs_nultidelivery = "{} Multi-Delivery" # Note: "nultidelivery" seems like a typo, assuming "Multi-Delivery"
gs_autorestore = "{} Auto-Restore Lots"
gs_autodisable = "{} Auto-Deactivate Lots"
gs_old_msg_mode = "{} Legacy Message Mode"
gs_keep_sent_messages_unread = "{} Don't mark as read when sending"

# Notification Settings
ns_new_msg = "{} New Message"
ns_cmd = "{} Command Received"
ns_new_order = "{} New Order"
ns_order_confirmed = "{} Order Confirmed"
ns_lot_activate = "{} Lot Restored"
ns_lot_deactivate = "{} Lot Deactivated"
ns_delivery = "{} Item Delivered"
ns_raise = "{} Lots Boosted"
ns_new_review = "{} New Review"
ns_bot_start = "{} Bot Started"
ns_other = "{} Other (Plugins)"

# Auto-Responder Settings
ar_edit_commands = "✏️ Edit Commands"
ar_add_command = "➕ New Command"
ar_to_ar = "🤖 To Auto-Responder Settings"
ar_to_mm = "Menu 🏠"
ar_edit_response = "✏️ Edit Response Text"
ar_edit_notification = "✏️ Edit Notification Text"
ar_notification = "{} Telegram Notification"
ar_add_more = "➕ Add More"
ar_add_another = "➕ Add Another"
ar_no_valid_commands_entered = "No valid commands were entered." # For auto_response_cp.py
ar_default_response_text = "The response for this command has not been configured yet. Please edit it." # For auto_response_cp.py
ar_default_notification_text = "User $username entered command: $message_text" # For auto_response_cp.py
ar_command_deleted_successfully = "Command/set '{command_name}' deleted successfully." # For auto_response_cp.py

# Auto-Delivery Settings
ad_edit_autodelivery = "🗳️ Edit Auto-Delivery"
ad_add_autodelivery = "➕ Link Auto-Delivery"
ad_add_another_ad = "➕ Link Another"
ad_add_more_ad = "➕ Link More"
ad_edit_goods_file = "📋 Item Files"
ad_upload_goods_file = "📤 Upload File"
ad_create_goods_file = "➕ Create File"
ad_to_ad = "📦 To Auto-Delivery Settings"
# ad_to_mm already exists above
never_updated = "never" # For auto_delivery_cp.py (last update time of FunPay lots list)
ad_default_response_text_new_lot = "Thanks for your purchase, $username!\nHere is your item:\n$product" # For auto_delivery_cp.py

# - Edit Auto-Delivery
ea_edit_delivery_text = "✏️ Edit Delivery Text"
ea_link_goods_file = "🔗 Link Item File"
ea_delivery = "{} Auto-Delivery"
ea_multidelivery = "{} Multi-Delivery"
ea_restore = "{} Auto-Restore"
ea_deactivate = "{} Auto-Deactivate"
ea_test = "🔑 Test Key"
ea_more_test = "🔑 More Keys"
ea_link_another_gf = "🔗 Another File"

# - Add Auto-Delivery
fl_manual = "✍️ Enter Manually"

# - Goods Files
gf_add_goods = "➕ Add Items"
gf_download = "📥 Download"
gf_create_another = "➕ Create Another"
gf_create_more = "➕ Create More"
gf_add_more = "➕ Add More"
gf_try_add_again = "➕ Try Again"
lot_info_header = "Lot Information" # For utils.py -> generate_lot_info_text
text_not_set = "(text not set)" # For utils.py -> generate_lot_info_text
gf_infinity = "infinite" # For utils.py -> generate_lot_info_text
gf_count_error = "count error" # For utils.py -> generate_lot_info_text
gf_file_not_found_short = "not found" # For utils.py -> generate_lot_info_text
gf_not_linked = "not linked" # For utils.py -> generate_lot_info_text
gf_file_created_now = "created" # For utils.py -> generate_lot_info_text (When file is just created by utility)
gf_file_creation_error_short = "creation error" # For utils.py -> generate_lot_info_text
no_lots_using_file = "No lots are using this file." # For auto_delivery_cp.py
gf_no_products_to_add = "No items were entered to be added." # For auto_delivery_cp.py
gf_deleted_successfully = "File {file_name} deleted successfully." # For auto_delivery_cp.py
gf_already_deleted = "File {file_name} was already deleted." # For auto_delivery_cp.py

# Blacklist Settings
bl_autodelivery = "{} Don't deliver item"
bl_autoresponse = "{} Don't respond to commands"
bl_new_msg_notifications = "{} No new message notifications"
bl_new_order_notifications = "{} No new order notifications"
bl_command_notifications = "{} No command notifications"

# Response Templates
tmplt_add = "➕ New Template"
tmplt_add_more = "➕ More Templates"
tmplt_add_another = "➕ Another Template"
tmplt_editing_header = "📝 Editing Template" # For templates_cp.py
tmplt_err_empty_text = "❌ Template text cannot be empty. Please enter text." # For templates_cp.py
tmplt_deleted_successfully = "✅ Template «{template_text}» deleted successfully." # For templates_cp.py

# Greeting Settings
gr_greetings = "{} Greet New Users"
gr_ignore_sys_msgs = "{} Ignore System Messages"
gr_edit_message = "✏️ Edit Greeting Text"
gr_edit_cooldown = "⏱️ Cooldown: {} days"

# Order Confirmation Response Settings
oc_watermark = "{} Watermark"
oc_send_reply = "{} Send Response"
oc_edit_message = "✏️ Edit Response Text"

# New Message Notification View Settings
mv_incl_my_msg = "{} My Messages"
mv_incl_fp_msg = "{} FunPay Messages"
mv_incl_bot_msg = "{} Bot Messages"
mv_only_my_msg = "{} Only Mine"
mv_only_fp_msg = "{} Only FunPay"
mv_only_bot_msg = "{} Only Bot"
mv_show_image_name = "{} Image Names"

# Plugins
pl_add = "➕ Add Plugin"
pl_activate = "🚀 Activate"
pl_deactivate = "💤 Deactivate"
pl_commands = "⌨️ Commands"
pl_settings = "⚙️ Settings"
pl_status_active = "Status: Active 🚀" # For plugins_cp.py
pl_status_inactive = "Status: Inactive 💤" # For plugins_cp.py
pl_no_commands = "This plugin has no registered commands." # For plugins_cp.py
pl_delete_handler_failed = "⚠️ Error executing delete handler for plugin '{plugin_name}'. The plugin was removed from the list, but its data or files might remain. Check logs." # For plugins_cp.py
pl_deleted_successfully = "✅ Plugin '{plugin_name}' deleted successfully. Restart FPCortex for changes to take effect." # For plugins_cp.py
pl_file_delete_error = "⚠️ Failed to delete plugin file '{plugin_path}'. Check permissions and logs." # For plugins_cp.py

# Configs
cfg_download_main = "📥 Main Config"
cfg_download_ar = "📥 Auto-Responder Config"
cfg_download_ad = "📥 Auto-Delivery Config"
cfg_upload_main = "📤 Main Config"
cfg_upload_ar = "📤 Auto-Responder Config"
cfg_upload_ad = "📤 Auto-Delivery Config"

# Authorized Users
tg_block_login = "{} Block login via password"

# Proxy
prx_proxy_add = "➕ Add Proxy"
proxy_status_enabled = "Enabled" # For proxy_cp.py
proxy_status_disabled = "Disabled" # For proxy_cp.py
proxy_check_status_enabled = "Enabled" # For proxy_cp.py
proxy_check_status_disabled = "Disabled" # For proxy_cp.py
proxy_not_used_currently = "not currently used" # For proxy_cp.py
proxy_not_selected = "not selected" # For proxy_cp.py
proxy_check_interval_info = "Auto-check interval: {interval} min." # For proxy_cp.py
proxy_global_status_header = "Global Proxy Module Status" # For proxy_cp.py
proxy_module_status_label = "Module State:" # For proxy_cp.py
proxy_health_check_label = "Auto-Proxy Check:" # For proxy_cp.py
proxy_current_in_use_label = "Current Proxy in Use:" # For proxy_cp.py
proxy_select_error_not_found = "⚠️ Error: This proxy no longer exists in the list." # For proxy_cp.py
proxy_select_error_invalid_format = "⚠️ Error: The selected proxy has an invalid format." # For proxy_cp.py
proxy_selected_and_applied = "✅ Proxy {proxy_str} selected and applied." # For proxy_cp.py
proxy_selected_not_applied = "ℹ️ Proxy {proxy_str} selected. Enable the proxy module in settings for it to be used." # For proxy_cp.py
proxy_deleted_successfully = "✅ Proxy {proxy_str} successfully removed from the list." # For proxy_cp.py
proxy_delete_error_not_found = "⚠️ Error: Proxy to be deleted not found in the list." # For proxy_cp.py

# Links
# Removed as per requirement

# Announcements (Disabled)
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
access_denied = "Hello, <b><i>{}</i></b>! 👋\n\nUnfortunately, you don't have access. ⛔\n\n" \
                "🔑 Enter the <u><b>secret password</b></u> (specified during initial setup) to log in."
access_granted = "Access granted! 🔓\n\n" \
                 "📢 Note: Notifications to <b><u>this chat</u></b> are not currently being sent.\n\n" \
                 "🔔 You can configure them in the menu.\n\n" \
                 "⚙️ Open <i>FPCortex</i> settings menu: /menu"
access_granted_notification = "<b>🚨 ATTENTION! 🚨\n\n\n</b>" * 3 + "\n\n\n🔐 User \"<a href=\"tg://user?id={1}\">{0}</a>\" " \
                                                                  "<b>(ID: {1}) has gained access to the Telegram control panel! 🔓</b>"
param_disabled = "❌ This setting is globally disabled and cannot be changed for this lot.\n\n" \
                 "🌍 Global settings are available here: " \
                 "/menu -> 🔧 General Settings."
old_mode_help = """<b>New Message Retrieval Mode</b> 🚀
✅ <i>FPCortex</i> sees the entire chat history and all details of new messages.
✅ <i>FPCortex</i> can see images and forward them to <i>Telegram</i>.
✅ <i>FPCortex</i> accurately identifies the author: you, the other person, or arbitration.
❌ The chat becomes "read" (doesn't glow orange) because <i>FPCortex</i> reads the entire history.

<b>Legacy Message Retrieval Mode</b> 🐢
✅ Chats you haven't read remain orange.
✅ Works slightly faster.
❌ <i>FPCortex</i> only sees the last message. If multiple messages arrive in succession, it only sees the last one.
❌ <i>FPCortex</i> cannot see images and cannot forward them.
❌ <i>FPCortex</i> doesn't always accurately identify the author. If the chat is unread, the message is from the other person; otherwise, it's from you. This logic can fail. Arbitration will also not be identified.

💡 If you press the <code>More Details</code> button in a notification, <i>FPCortex</i> will "read" the chat, show the last 15 messages (including images), and can accurately identify the author."""
bot_started = """✅ Telegram bot started!
You can <b><u>configure settings</u></b> and <b><u>use all <i>Telegram</i> bot functions</u></b>.

⏳ <i>FPCortex</i> <b><u>is not yet initialized</u></b>; its functions are inactive.
When <i>FPCortex</i> starts, this message will change.

🕒 If initialization takes a long time, check the logs with the /logs command."""
fpc_init = """✅ <b><u>FPCortex initialized!</u></b>
ℹ️ <b><i>Version:</i></b> <code>{}</code>
👑 <b><i>Account:</i></b>  <code>{}</code> | <code>{}</code>
💰 <b><i>Balance:</i></b> <code>{}₽, {}$, {}€</code>
📊 <b><i>Active Orders:</i></b>  <code>{}</code>

👨‍💻 <b><i>Author:</i></b> @beedge"""
create_test_ad_key = "Enter the lot name to test auto-delivery."
test_ad_key_created = """✅ A one-time key for delivering the lot «<code>{}</code>» has been created.
Send the command below in the chat with the buyer to deliver the item:
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
act_blacklist = """Enter the username to add to the blacklist."""
already_blacklisted = "❌ User <code>{}</code> is already on the blacklist."
user_blacklisted = "✅ User <code>{}</code> added to the blacklist."
act_unban = "Enter the username to remove from the blacklist."
not_blacklisted = "❌ User <code>{}</code> is not on the blacklist."
user_unbanned = "✅ User <code>{}</code> removed from the blacklist."
blacklist_empty = "🚫 The blacklist is empty."
act_proxy = "Enter proxy in the format <u>login:password@ip:port</u> or <u>ip:port</u>."
proxy_already_exists = "❌ Proxy <code>{}</code> already exists."
proxy_added = "✅ Proxy <u>{}</u> added successfully."
proxy_format = "❌ Invalid proxy format. Required: <u>login:password@ip:port</u> or <u>ip:port</u>."
proxy_adding_error = "⚠️ Error adding proxy."
proxy_undeletable = "❌ This proxy is in use and cannot be deleted."
act_edit_watermark = "Enter the new watermark text. Examples:\n{}\n<code>𝑭𝒖𝒏𝑷𝒂𝒚 𝑪𝒐𝒓𝒕𝒆𝒙</code>\n" \
                     "<code>FPCortex</code>\n<code>[FunPay / Cortex]</code>\n<code>𝑭𝑷𝑪𝒙</code>\n" \
                     "<code>FPCx</code>\n<code>🤖</code>\n<code>🧠</code>\n\n" \
                     "You can copy and edit the examples.\nNote that on FunPay, the 🧠 emoji " \
                     "may look different.\n\nTo remove the watermark, send <code>-</code>."
watermark_changed = "✅ Watermark changed."
watermark_deleted = "✅ Watermark removed."
watermark_error = "⚠️ Invalid watermark."
logfile_not_found = "❌ Log file not found."
logfile_sending = "Sending log file (this may take some time)... ⏳"
logfile_error = "⚠️ Failed to send log file."
logfile_deleted = "🗑️ Deleted {} log file(s)."
update_no_tags = "❌ Failed to get version list. Try again later. (Updates disabled)"
update_lasted = "✅ You have the latest version of FPCortex {} (Updates disabled)"
update_get_error = "❌ Failed to get information about the new version. Try again later. (Updates disabled)"
update_available = "<b>✨ New version available! ✨</b>\n\n\n{}\n\n{}"
update_update = "To update, enter the command /update (Updates disabled)"
update_backup = "✅ Backup created (configs, storage, plugins): <code>backup.zip</code>.\n\n" \
                "🔒 <b>IMPORTANT:</b> DO NOT SEND this archive to ANYONE. It contains all bot data and settings (including golden_key and items)."
update_backup_error = "⚠️ Failed to create backup."
update_backup_not_found = "❌ Backup not found."
update_downloaded = "✅ Update {} downloaded ({} items skipped). Installing... (Updates disabled)"
update_download_error = "⚠️ Error downloading update."
update_done = "✅ Update installed! Restart <i>FPCortex</i> with the /restart command (Updates disabled)"
update_done_exe = "✅ Update installed! New <code>FPCortex.exe</code> is in the <code>update</code> folder. " \
                  "Shut down <i>FPCortex</i>, replace the old <code>FPCortex.exe</code> with the new one, " \
                  "and run <code>Start.bat</code>. (Updates disabled)"
update_install_error = "⚠️ Error installing update."
restarting = "Restarting... 🚀"
power_off_0 = """<b>Are you sure you want to turn me off?</b> 🤔
You <b><u>won't be able</u></b> to turn me back on via <i>Telegram</i>!"""
power_off_1 = "One more time, just in case... <b><u>Are you absolutely sure about turning off?</u></b> 😟"
power_off_2 = """Just so you know:
You'll have to log into the server/computer and start me manually! 💻"""
power_off_3 = """Not insisting, but if you need to apply changes from the main config,
you can just restart me with the /restart command. 😉"""
power_off_4 = "Are you even reading my messages? 😉 Let's check: yes = no, no = yes. " \
              "I bet you're not even reading, and here I am writing important information."
power_off_5 = "So, your final answer is... yes? 😏"
power_off_6 = "Alright, alright, shutting down... 💤"
power_off_cancelled = "Shutdown cancelled. Continuing work! 👍"
power_off_error = "❌ This button is no longer relevant. Bring up the shutdown menu again."
enter_msg_text = "Enter the message text:"
msg_sent = "✅ Message sent to chat <a href=\"https://funpay.com/chat/?node={}\">{}</a>."
msg_sent_short = "✅ Message sent."
msg_sending_error = "⚠️ Failed to send message to chat <a href=\"https://funpay.com/chat/?node={}\">{}</a>."
msg_sending_error_short = "⚠️ Failed to send message."
send_img = "Send me an image 🖼️"
greeting_changed = "✅ Greeting text changed."
greeting_cooldown_changed = "✅ Greeting cooldown changed: {} days."
order_confirm_changed = "✅ Order confirmation response text changed!"
review_reply_changed = "✅ Response text for {}⭐ review changed!"
review_reply_empty = "⚠️ Response for {}⭐ review is not set."
review_reply_text = "Response for {}⭐ review:\n<code>{}</code>"
get_chat_error = "⚠️ Failed to get chat data."
viewing = "Viewing"
you = "You"
support = "Support"
photo = "Photo"
refund_attempt = "⚠️ Failed to refund order <code>#{}</code>. Attempts left: <code>{}</code>."
refund_error = "❌ Failed to refund order <code>#{}</code>."
refund_complete = "✅ Funds for order <code>#{}</code> refunded."
updating_profile = "Updating account statistics... 📊"
profile_updating_error = "⚠️ Failed to update statistics."
acc_balance_available = "available" # For utils.py -> generate_profile_text
act_change_golden_key = "🔑 Enter your golden_key:"
cookie_changed = "✅ golden_key successfully changed{}.\n"
cookie_changed2 = "Restart the bot with the /restart command to apply changes."
cookie_incorrect_format = "❌ Invalid golden_key format. Try again."
cookie_error = "⚠️ Failed to authenticate. Perhaps the entered golden_key is incorrect?"
ad_lot_not_found_err = "⚠️ Lot with index <code>{}</code> not found."
ad_already_ad_err = "⚠️ Auto-delivery is already configured for lot <code>{}</code>."
ad_lot_already_exists = "⚠️ Auto-delivery is already linked to lot <code>{}</code>."
ad_lot_linked = "✅ Auto-delivery linked to lot <code>{}</code>."
ad_link_gf = "Enter the name of the item file.\nTo unlink the file, send <code>-</code>\n\n" \
             "If the file doesn't exist, it will be created automatically."
ad_gf_unlinked = "✅ Item file unlinked from lot <code>{}</code>."
ad_gf_linked = "✅ File <code>storage/products/{}</code> linked to lot <code>{}</code>."
ad_gf_created_and_linked = "✅ File <code>storage/products/{}</code> <b><u>created</u></b> and linked to lot <code>{}</code>."
ad_creating_gf = "⏳ Creating file <code>storage/products/{}</code>..."
ad_product_var_err = "⚠️ An item file is linked to lot <code>{}</code>, but the delivery text lacks the <code>$product</code> variable."
ad_product_var_err2 = "⚠️ Cannot link file: the delivery text lacks the <code>$product</code> variable."
ad_text_changed = "✅ Delivery text for lot <code>{}</code> changed to:\n<code>{}</code>"
ad_updating_lots_list = "Updating lot and category data... ⏳"
ad_lots_list_updating_err = "⚠️ Failed to update lot and category data."
gf_not_found_err = "⚠️ Item file with index <code>{}</code> not found."
copy_lot_name = "Send the exact lot name (as on FunPay)."
act_create_gf = "Enter a name for the new item file (e.g., 'steam_keys')."
gf_name_invalid = "🚫 Invalid file name.\n\n" \
                  "Only <b><u>English</u></b> " \
                  "and <b><u>Russian</u></b> letters, numbers, and the symbols <code>_</code>, <code>-</code>, and <code>space</code> are allowed."
gf_already_exists_err = "⚠️ File <code>{}</code> already exists."
gf_creation_err = "⚠️ Error creating file <code>{}</code>."
gf_created = "✅ File <code>storage/products/{}</code> created."
gf_amount = "Items in file"
gf_uses = "Used in lots"
gf_send_new_goods = "Send items to add. Each item on a new line (<code>Shift+Enter</code>)."
gf_add_goods_err = "⚠️ Failed to add items to the file."
gf_new_goods = "✅ Added <code>{}</code> item(s) to file <code>storage/products/{}</code>."
gf_empty_error = "📂 File storage/products/{} is empty."
gf_linked_err = "⚠️ File <code>storage/products/{}</code> is linked to one or more lots.\n" \
                "Unlink it from all lots first, then delete."
gf_deleting_err = "⚠️ Failed to delete file <code>storage/products/{}</code>."
ar_cmd_not_found_err = "⚠️ Command with index <code>{}</code> not found."
ar_subcmd_duplicate_err = "⚠️ Command <code>{}</code> is duplicated in the set."
ar_cmd_already_exists_err = "⚠️ Command <code>{}</code> already exists."
ar_enter_new_cmd = "Enter a new command (or multiple, separated by <code>|</code>)."
ar_cmd_added = "✅ New command <code>{}</code> added."
ar_response_text = "Response text"
ar_notification_text = "Notification text"
ar_response_text_changed = "✅ Response text for command <code>{}</code> changed to:\n<code>{}</code>"
ar_notification_text_changed = "✅ Notification text for command <code>{}</code> changed to:\n<code>{}</code>"
cfg_main = "Main config. 🔒 IMPORTANT: DO NOT SEND this file to ANYONE."
cfg_ar = "Auto-responder config."
cfg_ad = "Auto-delivery config."
cfg_not_found_err = "⚠️ Config {} not found."
cfg_empty_err = "📂 Config {} is empty."
tmplt_not_found_err = "⚠️ Template with index <code>{}</code> not found."
tmplt_already_exists_err = "⚠️ This template already exists."
tmplt_added = "✅ Template added."
tmplt_msg_sent = "✅ Message sent using template to chat <a href=\"https://funpay.com/chat/?node={}\">{}</a>:\n\n<code>{}</code>"
pl_not_found_err = "⚠️ Plugin with UUID <code>{}</code> not found."
pl_file_not_found_err = "⚠️ File <code>{}</code> not found.\nRestart <i>FPCortex</i> with the /restart command."
pl_commands_list = "Commands for plugin <b><i>{}</i></b>:"
pl_author = "Author"
pl_new = "Send me the plugin file (.py).\n\n<b>☢️ WARNING!</b> Loading plugins from untrusted sources can be dangerous."
au_user_settings = "Settings for user {}"
adv_fpc = "😎 FPCortex - your best assistant for FunPay!"
adv_description = """🧠 FPCortex v{} 🚀

🤖 Auto-delivery of items
📈 Auto-boost lots
💬 Smart auto-responder
♻️ Auto-restore lots
📦 Auto-deactivation (if items run out)
🔝 Always online
📲 Telegram notifications
🕹️ Full control via Telegram
🧩 Plugin support
🌟 And much more!

👨‍💻 Author: @beedge"""

# - Menu Descriptions
desc_main = "Hello! Choose what you want to configure 👇"
desc_lang = "Select the interface language:"
desc_gs = "Here you can enable or disable the main functions of <i>FPCortex</i>."
desc_ns = """Configure notifications for this chat.
Each chat is configured separately!

ID of this chat: <code>{}</code>"""
desc_bl = "Set restrictions for users on the blacklist."
desc_ar = "Add commands for the auto-responder or edit existing ones."
desc_ar_list = "Select a command or command set to edit:"
desc_ad = "Auto-delivery settings: linking to lots, managing item files, etc."
desc_ad_list = "List of lots with configured auto-delivery. Select a lot to edit:"
desc_ad_fp_lot_list = "List of lots from your FunPay profile. Select a lot to configure auto-delivery.\n" \
                      "If the desired lot is missing, press <code>🔄 Refresh</code>.\n\n" \
                      "Last scan: {}"
desc_gf = "Select an item file to manage:"
desc_mv = "Configure how new message notifications will look."
desc_gr = "Configure welcome messages for new conversations.\n\n<b>Current greeting text:</b>\n<code>{}</code>"
desc_oc = "Configure the message sent upon order confirmation.\n\n<b>Current message text:</b>\n<code>{}</code>"
desc_or = "Configure automatic responses to reviews."
desc_an = "Announcement notification settings."
desc_cfg = "Here you can download or upload configuration files."
desc_tmplt = "Manage quick response templates."
desc_pl = "Plugin information and settings.\n\n" \
          "⚠️ <b>IMPORTANT:</b> After activating, deactivating, adding, or deleting a plugin, " \
          "you <b><u>must restart the bot</u></b> with the /restart command!"
desc_au = "User authorization settings for the Telegram control panel."
desc_proxy = "Manage proxy servers for bot operation."

# - Command Descriptions
cmd_menu = "open main menu"
cmd_language = "change interface language"
# profile_header_title = "Account Statistics" # Already exists as cmd_profile, but can be separate
cmd_profile = "view account statistics"
cmd_golden_key = "change golden_key (access token)"
cmd_test_lot = "create test auto-delivery key"
cmd_upload_chat_img = "(chat) upload image to FunPay"
cmd_upload_offer_img = "(lot) upload image to FunPay"
cmd_upload_plugin = "upload new plugin"
cmd_ban = "add user to blacklist"
cmd_unban = "remove user from blacklist"
cmd_black_list = "show blacklist"
cmd_watermark = "change message watermark"
cmd_logs = "download current log file"
cmd_del_logs = "delete old log files"
cmd_about = "about the bot"
cmd_check_updates = "check for updates"
cmd_update = "update the bot"
cmd_sys = "system information and load"
cmd_create_backup = "create backup"
cmd_get_backup = "download backup"
cmd_restart = "restart FPCortex"
cmd_power_off = "turn off FPCortex"

# - Variable Descriptions
v_edit_greeting_text = "Enter the greeting message text:"
v_edit_greeting_cooldown = "Enter the greeting cooldown (in days, e.g., 0.5 for 12 hours):"
v_edit_order_confirm_text = "Enter the order confirmation response text:"
v_edit_review_reply_text = "Enter the response text for a {}⭐ review:"
v_edit_delivery_text = "Enter the new text for item auto-delivery:"
v_edit_response_text = "Enter the new response text for the command:"
v_edit_notification_text = "Enter the new text for the Telegram notification:"
V_new_template = "Enter the text for the new response template:"
v_list = "Available variables:"
v_date = "<code>$date</code> - date (DD.MM.YYYY)"
v_date_text = "<code>$date_text</code> - date (January 1)"
v_full_date_text = "<code>$full_date_text</code> - date (January 1, 2001)"
v_time = "<code>$time</code> - time (HH:MM)"
v_full_time = "<code>$full_time</code> - time (HH:MM:SS)"
v_photo = "<code>$photo=[PHOTO_ID]</code> - image (ID via /upload_chat_img)"
v_sleep = "<code>$sleep=[SECONDS]</code> - delay before sending (e.g., $sleep=2)"
v_order_id = "<code>$order_id</code> - order ID (without #)"
v_order_link = "<code>$order_link</code> - link to the order"
v_order_title = "<code>$order_title</code> - order title"
v_order_params = "<code>$order_params</code> - order parameters"
v_order_desc_and_params = "<code>$order_desc_and_params</code> - order title and/or parameters"
v_order_desc_or_params = "<code>$order_desc_or_params</code> - order title or parameters"
v_game = "<code>$game</code> - game name"
v_category = "<code>$category</code> - subcategory name"
v_category_fullname = "<code>$category_fullname</code> - full name (subcategory + game)"
v_product = "<code>$product</code> - item from file (if not linked, won't be replaced)"
v_chat_id = "<code>$chat_id</code> - chat ID"
v_chat_name = "<code>$chat_name</code> - chat name"
v_message_text = "<code>$message_text</code> - message text from the other person"
v_username = "<code>$username</code> - nickname of the other person"

# Exception Texts
exc_param_not_found = "Parameter \"{}\" not found."
exc_param_cant_be_empty = "Value of parameter \"{}\" cannot be empty."
exc_param_value_invalid = "Invalid value for \"{}\". Allowed: {}. Current: \"{}\"."
exc_goods_file_not_found = "Item file \"{}\" not found."
exc_goods_file_is_empty = "File \"{}\" is empty."
exc_not_enough_items = "Not enough items in file \"{}\". Needed: {}, available: {}."
exc_no_product_var = "\"productsFileName\" specified, but the \"response\" parameter lacks the $product variable."
exc_no_section = "Section is missing."
exc_section_duplicate = "Duplicate section detected."
exc_cmd_duplicate = "Command or sub-command \"{}\" already exists."
exc_cfg_parse_err = "Error in config {}, section [{}]: {}"
exc_plugin_field_not_found = "Failed to load plugin \"{}\": missing required field \"{}\"."

# Logs (kept mostly as is for developer context, only text translated)
log_tg_initialized = "$MAGENTATelegram bot initialized."
log_tg_started = "$CYANTelegram bot $YELLOW@{}$CYAN started."
log_tg_handler_error = "An error occurred while executing a Telegram bot handler."
log_tg_update_error = "An error ({}) occurred while getting Telegram updates (invalid token entered?)."
log_tg_notification_error = "An error occurred while sending notification to chat $YELLOW{}$RESET."
log_access_attempt = "$MAGENTA@{} (ID: {})$RESET tried to access the control panel. Holding them back!"
log_click_attempt = "$MAGENTA@{} (ID: {})$RESET is clicking control panel buttons in chat $MAGENTA@{} (ID: {})$RESET. It won't work!"
log_access_granted = "$MAGENTA@{} (ID: {})$RESET gained access to the control panel."
log_new_ad_key = "$MAGENTA@{} (ID: {})$RESET created a key for delivering $YELLOW{}$RESET: $CYAN{}$RESET."
log_user_blacklisted = "$MAGENTA@{} (ID: {})$RESET added $YELLOW{}$RESET to the blacklist."
log_user_unbanned = "$MAGENTA@{} (ID: {})$RESET removed $YELLOW{}$RESET from the blacklist."
log_watermark_changed = "$MAGENTA@{} (ID: {})$RESET changed the message watermark to $YELLOW{}$RESET."
log_watermark_deleted = "$MAGENTA@{} (ID: {})$RESET removed the message watermark."
log_greeting_changed = "$MAGENTA@{} (ID: {})$RESET changed the greeting text to $YELLOW{}$RESET."
log_greeting_cooldown_changed = "$MAGENTA@{} (ID: {})$RESET changed the greeting message cooldown to $YELLOW{}$RESET days."
log_order_confirm_changed = "$MAGENTA@{} (ID: {})$RESET changed the order confirmation response text to $YELLOW{}$RESET."
log_review_reply_changed = "$MAGENTA@{} (ID: {})$RESET changed the response text for a {} star review to $YELLOW{}$RESET."
log_param_changed = "$MAGENTA@{} (ID: {})$RESET changed parameter $CYAN{}$RESET of section $YELLOW[{}]$RESET to $YELLOW{}$RESET."
log_notification_switched = "$MAGENTA@{} (ID: {})$RESET switched $YELLOW{}$RESET notifications for chat $YELLOW{}$RESET to $CYAN{}$RESET."
log_ad_linked = "$MAGENTA@{} (ID: {})$RESET linked auto-delivery to lot $YELLOW{}$RESET."
log_ad_text_changed = "$MAGENTA@{} (ID: {})$RESET changed the delivery text for lot $YELLOW{}$RESET to $YELLOW\"{}\"$RESET."
log_ad_deleted = "$MAGENTA@{} (ID: {})$RESET deleted auto-delivery for lot $YELLOW{}$RESET."
log_gf_created = "$MAGENTA@{} (ID: {})$RESET created item file $YELLOWstorage/products/{}$RESET."
log_gf_unlinked = "$MAGENTA@{} (ID: {})$RESET unlinked item file from lot $YELLOW{}$RESET."
log_gf_linked = "$MAGENTA@{} (ID: {})$RESET linked item file $YELLOWstorage/products/{}$RESET to lot $YELLOW{}$RESET."
log_gf_created_and_linked = "$MAGENTA@{} (ID: {})$RESET created and linked item file $YELLOWstorage/products/{}$RESET to lot $YELLOW{}$RESET."
log_gf_new_goods = "$MAGENTA@{} (ID: {})$RESET added $CYAN{}$RESET item(s) to file $YELLOWstorage/products/{}$RESET."
log_gf_downloaded = "$MAGENTA@{} (ID: {})$RESET requested item file $YELLOWstorage/products/{}$RESET."
log_gf_deleted = "$MAGENTA@{} (ID: {})$RESET deleted item file $YELLOWstorage/products/{}$RESET."
log_ar_added = "$MAGENTA@{} (ID: {})$RESET added new command $YELLOW{}$RESET."
log_ar_response_text_changed = "$MAGENTA@{} (ID: {})$RESET changed the response text for command $YELLOW{}$RESET to $YELLOW\"{}\"$RESET."
log_ar_notification_text_changed = "$MAGENTA@{} (ID: {})$RESET changed the notification text for command $YELLOW{}$RESET to $YELLOW\"{}\"$RESET."
log_ar_cmd_deleted = "$MAGENTA@{} (ID: {})$RESET deleted command $YELLOW{}$RESET."
log_cfg_downloaded = "$MAGENTA@{} (ID: {})$RESET requested config $YELLOW{}$RESET."
log_tmplt_added = "$MAGENTA@{} (ID: {})$RESET added response template $YELLOW\"{}\"$RESET."
log_tmplt_deleted = "$MAGENTA@{} (ID: {})$RESET deleted response template $YELLOW\"{}\"$RESET."
log_pl_activated = "$MAGENTA@{} (ID: {})$RESET activated plugin $YELLOW\"{}\"$RESET."
log_pl_deactivated = "$MAGENTA@{} (ID: {})$RESET deactivated plugin $YELLOW\"{}\"$RESET."
log_pl_deleted = "$MAGENTA@{} (ID: {})$RESET deleted plugin $YELLOW\"{}\"$RESET."
log_pl_delete_handler_err = "An error occurred while executing the delete handler for plugin $YELLOW\"{}\"$RESET."

# Handler Logs
log_new_msg = "$MAGENTA┌──$RESET New message in conversation with user $YELLOW{} (CID: {}):"
log_sending_greetings = "User $YELLOW{} (CID: {})$RESET wrote for the first time! Sending greeting message..."
log_new_cmd = "Received command $YELLOW{}$RESET in chat with user $YELLOW{} (CID: {})$RESET."
ntfc_new_order = "💰 <b>New Order:</b> <code>{}</code>\n\n<b><i>🙍‍♂️ Buyer:</i></b>  <code>{}</code>\n" \
                 "<b><i>💵 Amount:</i></b>  <code>{}</code>\n<b><i>📇 ID:</i></b> <code>#{}</code>\n\n<i>{}</i>"
ntfc_new_order_not_in_cfg = "ℹ️ Item will not be delivered because auto-delivery is not linked to the lot."
ntfc_new_order_ad_disabled = "ℹ️ Item will not be delivered because auto-delivery is disabled in global switches."
ntfc_new_order_ad_disabled_for_lot = "ℹ️ Item will not be delivered because auto-delivery is disabled for this lot."
ntfc_new_order_user_blocked = "ℹ️ Item will not be delivered because the user is blacklisted and auto-delivery blocking is enabled."
ntfc_new_order_will_be_delivered = "ℹ️ Item will be delivered shortly."
ntfc_new_review = "🔮 You received {} for order <code>{}</code>!\n\n💬<b>Review:</b>\n<code>{}</code>{}"
ntfc_review_reply_text = "\n\n🗨️<b>Reply:</b> \n<code>{}</code>"

# Cortex Logs
crd_proxy_detected = "Proxy detected."
crd_checking_proxy = "Checking proxy..."
crd_proxy_err = "Failed to connect to proxy. Ensure the details are correct."
crd_proxy_success = "Proxy checked successfully! IP address: $YELLOW{}$RESET."
crd_acc_get_timeout_err = "Failed to load account data: request timed out."
crd_acc_get_unexpected_err = "An unexpected error occurred while getting account data."
crd_try_again_in_n_secs = "Retrying in {} second(s)..."
crd_getting_profile_data = "Getting lot and category data..."
crd_profile_get_timeout_err = "Failed to load account lot data: request timed out."
crd_profile_get_unexpected_err = "An unexpected error occurred while getting lot and category data."
crd_profile_get_too_many_attempts_err = "An error occurred while getting lot and category data: maximum attempts ({}) exceeded."
crd_profile_updated = "Updated information about profile lots $YELLOW({})$RESET and categories $YELLOW({})$RESET."
crd_tg_profile_updated = "Updated information about profile lots $YELLOW({})$RESET and categories $YELLOW({})$RESET (TG CP)."
crd_raise_time_err = 'Failed to boost lots in category $CYAN\"{}\"$RESET. FunPay says: "{}". Next attempt in {}.'
crd_raise_unexpected_err = "An unexpected error occurred while trying to boost lots in category $CYAN\"{}\"$RESET. Pausing for 10 seconds..."
crd_raise_status_code_err = "Error {} while boosting lots in category $CYAN\"{}\"$RESET. Pausing for 1 min..."
crd_lots_raised = "All lots in category $CYAN\"{}\"$RESET boosted!"
crd_raise_wait_3600 = "Next attempt in {}."
crd_msg_send_err = "An error occurred while sending message to chat $YELLOW{}$RESET."
crd_msg_attempts_left = "Attempts left: $YELLOW{}$RESET."
crd_msg_no_more_attempts_err = "Failed to send message to chat $YELLOW{}$RESET: maximum attempts exceeded."
crd_msg_sent = "Sent message to chat $YELLOW{}."
crd_session_timeout_err = "Failed to refresh session: request timed out."
crd_session_unexpected_err = "An unexpected error occurred while refreshing session."
crd_session_no_more_attempts_err = "Failed to refresh session: maximum attempts exceeded."
crd_session_updated = "Session refreshed."
crd_raise_loop_started = "$CYANAuto-boost loop started (this does not mean auto-boost is enabled)."
crd_raise_loop_not_started = "$CYANAuto-boost loop was not started as no lots were found on the account."
crd_session_loop_started = "$CYANSession refresh loop started."
crd_no_plugins_folder = "Plugins folder not found."
crd_no_plugins = "No plugins found."
crd_plugin_load_err = "Failed to load plugin {}."
crd_invalid_uuid = "Failed to load plugin {}: invalid UUID."
crd_uuid_already_registered = "UUID {} ({}) is already registered."
crd_handlers_registered = "Handlers from $YELLOW{}.py$RESET registered."
crd_handler_err = "An error occurred while executing a handler."
crd_tg_au_err = "Failed to edit message with user info: {}. Trying without link."

# New keys added during redesign:

# For utils.py -> generate_profile_text
# profile_header_title = "Account Statistics" # Already exists as cmd_profile
# acc_balance_available = "available" # Already exists above

# For utils.py -> generate_lot_info_text
# lot_info_header = "Lot Information" # Already exists above
# text_not_set = "(text not set)" # Already exists above
# gf_infinity = "infinite" # Already exists above
# gf_count_error = "count error" # Already exists above
# gf_file_not_found_short = "not found" # Already exists above
# gf_not_linked = "not linked" # Already exists above
# gf_file_created_now = "created" # Already exists above
# gf_file_creation_error_short = "creation error" # Already exists above

# For auto_delivery_cp.py
# never_updated = "never" # Already exists above
# ad_default_response_text_new_lot = "Thanks for your purchase, $username!\nHere is your item:\n$product" # Already exists above
# no_lots_using_file = "No lots are using this file." # Already exists above
# gf_no_products_to_add = "No items were entered to be added." # Already exists above
# gl_refresh_and_try_again = "Refresh the list and try again." # Already exists above
# gf_deleted_successfully = "File {file_name} deleted successfully." # Already exists above
# gf_already_deleted = "File {file_name} was already deleted." # Already exists above

# For auto_response_cp.py
# ar_no_valid_commands_entered = "No valid commands were entered." # Already exists above
# ar_default_response_text = "The response for this command has not been configured yet. Please edit it." # Already exists above
# ar_default_notification_text = "User $username entered command: $message_text" # Already exists above
# ar_command_deleted_successfully = "Command/set '{command_name}' deleted successfully." # Already exists above

# For file_uploader.py
file_err_not_detected = "❌ File not found in the message."
file_err_must_be_text = "❌ The file must be a text file (e.g., .txt, .cfg, .py, .json, .ini, .log)."
file_err_wrong_format = "❌ Invalid file format: <b><u>.{actual_ext}</u></b> (expected <b><u>.{expected_ext}</u></b>)."
file_err_too_large = "❌ File size must not exceed 20MB."
file_info_downloading = "⏬ Downloading file from Telegram servers..."
file_err_download_failed = "❌ An error occurred while downloading the file to the bot server."
file_info_checking_validity = "🤔 Checking file content..."
file_err_processing_generic = "⚠️ An error occurred while processing the file: <code>{error_message}</code>"
file_err_utf8_decode = "An error occurred while reading the file (UTF-8). Ensure the file encoding is UTF-8 and line endings are LF."
file_info_main_cfg_loaded = "✅ Main config loaded successfully.\n\n⚠️ <b>Bot restart required (/restart)</b> for changes to take effect.\n\nAny changes to the main config via control panel switches before restarting will override the loaded settings."
file_info_ar_cfg_applied = "✅ Auto-responder config loaded and applied successfully."
file_info_ad_cfg_applied = "✅ Auto-delivery config loaded and applied successfully."
plugin_uploaded_success = "✅ Plugin <code>{filename}</code> uploaded successfully.\n\n⚠️ To make the plugin work, <b><u>restart FPCortex</u></b> using the /restart command!"
image_upload_unsupported_format = "❌ Unsupported image format. Allowed: <code>.png</code>, <code>.jpg</code>, <code>.jpeg</code>, <code>.gif</code>."
image_upload_error_generic = "⚠️ Failed to upload image to FunPay. Check the log file (<code>logs/log.log</code>) for details."
image_upload_chat_success_info = "Use this ID in auto-delivery or auto-responder texts with the <code>$photo</code> variable.\n\nExample: <code>$photo={image_id}</code>"
image_upload_offer_success_info = "Use this ID to add images to your lots on FunPay."
image_upload_success_header = "✅ Image successfully uploaded to FunPay server.\n\n<b>Image ID:</b> <code>{image_id}</code>\n\n"
products_file_provide_prompt = "📎 Send me the item file (in .txt format):"
products_file_upload_success = "✅ Item file <code>{filepath}</code> uploaded successfully.\nNumber of items in file: <code>{count}</code>."
products_file_count_error = "⚠️ An error occurred while counting items in the uploaded file. The file was uploaded, but please check its contents."
main_config_provide_prompt = "⚙️ Send me the main config file (<code>_main.cfg</code>):"
ar_config_provide_prompt = "🤖 Send me the auto-responder config file (<code>auto_response.cfg</code>):"
ad_config_provide_prompt = "📦 Send me the auto-delivery config file (<code>auto_delivery.cfg</code>):"

# For plugins_cp.py
# pl_status_active = "Status: Active 🚀" # Already exists above
# pl_status_inactive = "Status: Inactive 💤" # Already exists above
# pl_no_commands = "This plugin has no registered commands." # Already exists above
# pl_delete_handler_failed = "..." # Already exists above
# pl_deleted_successfully = "..." # Already exists above
# pl_file_delete_error = "..." # Already exists above

# For proxy_cp.py
# proxy_status_enabled = "Enabled" # Already exists above
# proxy_status_disabled = "Disabled" # Already exists above
# proxy_check_status_enabled = "Enabled" # Already exists above
# proxy_check_status_disabled = "Disabled" # Already exists above
# proxy_not_used_currently = "not currently used" # Already exists above
# proxy_not_selected = "not selected" # Already exists above
# proxy_check_interval_info = "Auto-check interval: {interval} min." # Already exists above
# proxy_global_status_header = "Global Proxy Module Status" # Already exists above
# proxy_module_status_label = "Module State:" # Already exists above
# proxy_health_check_label = "Auto-Proxy Check:" # Already exists above
# proxy_current_in_use_label = "Current Proxy in Use:" # Already exists above
# proxy_select_error_not_found = "..." # Already exists above
# proxy_select_error_invalid_format = "..." # Already exists above
# proxy_selected_and_applied = "..." # Already exists above
# proxy_selected_not_applied = "..." # Already exists above
# proxy_deleted_successfully = "..." # Already exists above
# proxy_delete_error_not_found = "..." # Already exists above

# For templates_cp.py
# tmplt_editing_header = "📝 Editing Template" # Already exists above
# tmplt_err_empty_text = "..." # Already exists above
# tmplt_deleted_successfully = "..." # Already exists above

# END OF FILE FunPayCortex/locales/en.py