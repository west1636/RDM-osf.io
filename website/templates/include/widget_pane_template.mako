<%page args="displayInDrawer, render_addon_widget, addons_widget_data"/>

<% addons_count = 0 %>
% for addon in ['sparql', 'restfulapi', 'ftp',]:
  % if displayInDrawer[addon] and addons_widget_data[addon]:
    <% addons_count += 1 %>
  % endif
% endfor

<div class="scripted widget-pane">

  % if addons_count > 0:
  <div class="widget-handle-div widget-handle pull-right pointer visible-lg visible-md"
    data-toggle="tooltip" data-placement="bottom" title="Addons">
    <i class="fa fa-cubes fa-2x widget-handle-icon"></i>
  </div>
  <div class="widget-bar"></div>


  <div class="widget-sidebar">
    <div class="widget-sidebar-content">
      <button type="button" class="close text-smaller" data-bind="click: togglePane">
        <i class="fa fa-times"></i>
      </button>
      <div data-bind="stopBinding: true">
      % for addon in ['sparql', 'restfulapi', 'ftp',]:
        % if displayInDrawer[addon] and addons_widget_data[addon]:
          ${ render_addon_widget.render_addon_widget(addon, addons_widget_data[addon]) }
        % endif
      % endfor
      </div>
    </div>
  </div>
  % endif

</div>
