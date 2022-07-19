<%!
    from website import settings
    from datetime import datetime
%>
<!doctype html>
<html class="no-js" lang="">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <meta name="description" content="National Institute of Informatics Notifications">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body leftmargin="0" marginwidth="0" topmargin="0" marginheight="0" offset="0" style="-webkit-text-size-adjust: none;font-family: 'Helvetica', sans-serif;background: #eeeeee;padding: 0;margin: 0;border: none;list-style: none;width: 100% !important;">
    <table id="layout-table" width="100%" border="0" cellpadding="0" cellspacing="0">
        <tr>
            <td style="border-collapse: collapse;">
                <table id="layout-table" width="100%" border="0" cellpadding="10" cellspacing="0" height="100%">
                    <tbody>
                        <tr class="banner" style="background: #214762;color: white;">
                            <td class="text-center" style="border-collapse: collapse;text-align: center;">
                                <table id="header-logo" border="0" style="margin: 0 auto;padding: 0px;">
                                    <tr>
                                        <td style="border-collapse: collapse;">
                                            % if context.get('logo', settings.OSF_LOGO) not in settings.OSF_LOGO_LIST:
                                                <img src="https://raw.githubusercontent.com/CenterForOpenScience/osf-assets/master/files/preprints-assets/${context.get('logo')}/wide_white.png" alt="GakuNin RDM logo" style="border: 0;height: auto;line-height: 100%;outline: none;text-decoration: none;">
                                            %else:
                                                <img src="https://rdm.nii.ac.jp/static/img/${context.get('logo', settings.OSF_LOGO)}.png" alt="GakuNin RDM logo" style="border: 0;height: auto;line-height: 100%;outline: none;text-decoration: none;">
                                            % endif
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </td>
        </tr>
        <tr>
          <td style="border-collapse: collapse;">
            <table width="600" border="0" cellpadding="25" cellspacing="0" align="center" style="margin: 30px auto 0 auto;background: white;box-shadow: 0 0 2px #ccc;">
              <tbody>
                <tr>
                  <td style="border-collapse: collapse;">
                  The Japanese statement will be followed by an English statement.<br>
                  </td>
                </tr>
              </tbody>
            </table>
            <table id="content" width="600" border="0" cellpadding="25" cellspacing="0" align="center" style="margin: 30px auto 0 auto;background: white;box-shadow: 0 0 2px #ccc;">
              <tbody>
                ${self.content()}
              </tbody>
            </table>
            % if context.get('can_change_preferences', True):
            <table width="600" border="0" cellpadding="25" cellspacing="0" align="center" style="margin: 30px auto 0 auto;background: white;box-shadow: 0 0 2px #ccc;">
                <tbody>
                    <tr>
                        <td style="border-collapse: collapse;">
                            % if context.get('is_reviews_moderator_notification', False):
                                <p class="text-smaller text-center" style="text-align: center;font-size: 12px;">
                                  % if not context.get('referrer', False):
                                        本メールは${provider_name}の${'管理者' if is_admin else 'a モデレータ'}に送信されています。
                                    % endif
                                    モデレーション通知の設定は
                                    <a href=${notification_settings_url}>通知設定</a>から変更できます。
                                </p>
                                <p class="text-smaller text-center" style="text-align: center;font-size: 12px;">
                                  % if not context.get('referrer', False):
                                        You are receiving these emails because you are ${'an administrator' if is_admin else 'a moderator'} on ${provider_name}.
                                    % endif
                                    To change your moderation notification preferences,
                                    visit your <a href=${notification_settings_url}>notification settings</a>.
                                </p>
                            % else:
                                <p class="text-smaller text-center" style="text-align: center;font-size: 12px;">メール受信頻度を変更するには、
                                    % if context.get('can_change_node_preferences', False) and node:
                                        <a href="${settings.DOMAIN + node._id + '/settings#configureNotificationsAnchor'}">プロジェクトのメール設定</a>あるいは
                                    % endif
                                    あなたの<a href="${settings.DOMAIN + "settings/notifications/"}">ユーザー設定</a>からデフォルトのメール設定を変更してください。
                                </p>
                                <p class="text-smaller text-center" style="text-align: center;font-size: 12px;">To change how often you receive emails, visit
                                    % if context.get('can_change_node_preferences', False) and node:
                                        this <a href="${settings.DOMAIN + node._id + '/settings#configureNotificationsAnchor'}">project's settings</a> for emails about this project or
                                    % endif
                                    your <a href="${settings.DOMAIN + "settings/notifications/"}">user settings</a> to manage default email settings.
                                </p>
                            % endif
                        </td>
                    </tr>
                </tbody>
            </table>
            % endif
          </td>
        </tr>
        <tr>
            <td style="border-collapse: collapse; padding-top: 15px;">
                <table width="80%" border="0" cellpadding="10" cellspacing="0" align="center" class="footer" style="margin-top: 45px;padding: 25px 0 35px;background-color: rgb(244, 244, 244);border-top: 1px solid #E5E5E5;border-bottom: 1px solid #E5E5E5;width: 100%;color: #555;">
                    <tbody>
                        <tr>
                            <td style="border-collapse: collapse;">
                                <p class="text-smaller text-center" style="text-align: center;font-size: 12px;">Copyright &copy; 2016-${datetime.utcnow().year} 国立情報学研究所 |
                                    <a href="https://support.rdm.nii.ac.jp/terms/">プライバシーポリシー</a>
                                </p>
                                <p class="text-smaller text-center" style="text-align: center;font-size: 12px;">〒101-8430 東京都千代田区一ツ橋2-1-2</p>
                                <p class="text-smaller text-center" style="text-align: center;font-size: 12px;">Copyright &copy; 2016-${datetime.utcnow().year} National Institute of Informatics |
                                    <a href="https://support.rdm.nii.ac.jp/terms/">Privacy Policy</a>
                                </p>
                                <p class="text-smaller text-center" style="text-align: center;font-size: 12px;">2-1-2 Hitotsubashi, Chiyoda Ward, Tokyo 101-8430, JAPAN</p>
                                <p class="text-smaller text-center" style="text-align: center;font-size: 12px;">${self.footer()}</p>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>

<%def name="content()">

</%def>

<%def name="footer()">

</%def>
