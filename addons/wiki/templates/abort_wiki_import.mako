<!-- Abort Wiki Import Modal -->
<div class="modal fade" id="abortWikiImport">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                <h3 class="modal-title">${_("Abort wiki import")}</h3>
            </div><!-- end modal-header -->
            <div class="modal-body">
                <div id="alert" style="padding-bottom:10px">${_("Any wiki imports in process will be aborted. This action is irreversible.")}</div>
            </div><!-- end modal-body -->
            <div class="modal-footer">
                <a id="close" href="#" class="btn btn-default" data-dismiss="modal">${_("Cancel")}</a>
                <a id="abort-wiki-import" class="btn btn-danger">${_("Abort")}</a>
            </div><!-- end modal-footer -->
        </div><!-- end modal- content -->
    </div><!-- end modal-dialog -->
</div><!-- end modal -->

<script type="text/javascript">
    $(document).ready(function() {
        $('#abort-wiki-import').on('click', function () {

            var cleanTasksUrl = ${ urls['api']['base'] | sjson, n } + 'clean_celery_tasks/';
            $.ajax({
                type: 'POST',
                cache: false,
                url: cleanTasksUrl,
                dataType: 'json',
            }).done(function (response) {
                const reloadUrl = (location.href).replace(location.search, '')
                window.location.assign(reloadUrl);
            })
        });
    });
</script>
