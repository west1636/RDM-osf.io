<!-- Sort Component Modal -->
<div class="modal fade" id="sortWiki">
    <div class="modal-dialog" style="width: 70%;">
        <div class="modal-content">
            <form class="form">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                    <h3 draggable="true" class="modal-title">${_("Sort Wiki Tree")}</h3>
                </div><!-- end modal-header -->
                <div class="modal-body" style="height: 550px; overflow: auto;">
                    <div id="manageWikitree" class="scripted">
                        <ul style="margin-top: 40px;" data-bind="sortable: {template: 'wikitreeRow', data: $root.data, afterMove: $root.afterMove}"></ul>
                    </div>
                </div><!-- end modal-body -->
                <div class="modal-footer">
                    <a id="close" class="btn btn-default" data-dismiss="modal">${_("Cancel")}</a>
                    <button id="treeSave" data-bind="click: submit" id="add-wiki-submit" type="submit" class="btn btn-success">${_("Save")}</button>
                </div><!-- end modal-footer -->
            </form>
        </div><!-- end modal- content -->
    </div><!-- end modal-dialog -->
</div><!-- end modal -->

<script id="wikitreeRow" type="text/html">
  <li class="ko-item" data-bind="attr: {class: $parent.id}, event: { mousedown: $root.mouseDown}">
    <!-- ko if: $data.name -->
    <div style="margin-bottom: 10px;" data-bind="attr: {class: 'sort-item', id: $data.id}, event: { click: $root.expandOrCollapse}">
    <!-- ko if: $data.children().length -->
    <div style="display: inline;"><i class="fa fa-angle-down"></i></div>
    <!-- /ko -->
    <!-- ko ifnot: $data.children().length -->
    <div style="display: inline;"><i></i></div>
    <!-- /ko -->
    <div style="display: inline;"><a href="#" data-bind="text: $data.name"></a></div>
    </div>
    <!-- /ko -->
    <!-- ko if: $data.children -->
    <ul class="sort-children" data-bind="sortable: { template: 'wikitreeRow', data: $data.children, afterMove: $root.afterMove}"></ul>
    <!-- /ko -->
  </li>
</script>
