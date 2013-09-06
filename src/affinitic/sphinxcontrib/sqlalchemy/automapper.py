# -*- coding: utf-8 -*-
import sphinx.ext.autodoc
import sphinx.domains.python
import sphinx.roles
from sphinx.ext.autodoc import ALL
from sphinx.util import force_decode
from sphinx.util.docstrings import prepare_docstring
from sphinx.locale import l_

from affinitic.db.mapper import MappedClassBase


class MapperDocumenter(sphinx.ext.autodoc.ClassDocumenter):
    objtype = 'mapper'

    # Since these have very specific tests, we give the classes defined here
    # very high priority so that they override any other documenters.
    priority = 100 + sphinx.ext.autodoc.ClassDocumenter.priority

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        return isinstance(member, MappedClassBase)

    def format_args(self):
        return self.object.getSignatureString()

    def get_object_members(self, want_all):
        """
        Return `(members_check_module, members)` where `members` is a
        list of `(membername, member)` pairs of the members of *self.object*.

        If *want_all* is True, return all members.  Else, only return those
        members given by *self.options.members* (which may also be none).
        """
        obj = self.object
        return False, [(col.name, col) for col in obj.__table__.c]

    def filter_members(self, members, want_all):
        """Filter the given member list.

        Members are skipped if

        - they are private (except if given explicitly or the private-members
          option is set)
        - they are special methods (except if given explicitly or the
          special-members option is set)
        - they are undocumented (except if the undoc-members option is set)

        The user can override the skipping decision by connecting to the
        ``autodoc-skip-member`` event.
        """
        ret = []

        # search for members in source code too
        namespace = '.'.join(self.objpath)  # will be empty for modules

        if self.analyzer:
            attr_docs = self.analyzer.find_attr_docs()
        else:
            attr_docs = {}

        # process members and determine which to skip
        for (membername, member) in members:
            # if isattr is True, the member is documented as an attribute
            isattr = False

            doc = self.get_attr(member, 'doc', None)
            if doc is None:
                doc = self.get_attr(member, '__doc__', None)
            # if the member __doc__ is the same as self's __doc__, it's just
            # inherited and therefore not the member's doc
            cls = self.get_attr(member, '__class__', None)
            if cls:
                cls_doc = self.get_attr(cls, '__doc__', None)
                if cls_doc == doc:
                    doc = None
            has_doc = bool(doc)

            keep = False
            if want_all and membername.startswith('__') and \
                   membername.endswith('__') and len(membername) > 4:
                # special __methods__
                if self.options.special_members is ALL and \
                        membername != '__doc__':
                    keep = has_doc or self.options.undoc_members
                elif self.options.special_members and \
                     self.options.special_members is not ALL and \
                        membername in self.options.special_members:
                    keep = has_doc or self.options.undoc_members
            elif want_all and membername.startswith('_'):
                # ignore members whose name starts with _ by default
                keep = self.options.private_members and \
                       (has_doc or self.options.undoc_members)
            elif (namespace, membername) in attr_docs:
                # keep documented attributes
                keep = True
                isattr = True
            else:
                # ignore undocumented members if :undoc-members: is not given
                keep = has_doc or self.options.undoc_members

            # give the user a chance to decide whether this member
            # should be skipped
            if self.env.app:
                # let extensions preprocess docstrings
                skip_user = self.env.app.emit_firstresult(
                    'autodoc-skip-member', self.objtype, membername, member,
                    not keep, self.options)
                if skip_user is not None:
                    keep = not skip_user

            if keep:
                ret.append((membername, member, isattr))

        return ret


class ColumnAttributeDocumenter(sphinx.ext.autodoc.AttributeDocumenter):
    objtype = 'columnattribute'   # Called 'autointerfaceattribute'
    directivetype = 'attribute'      # Formats as a 'attribute' for now
    priority = 100 + sphinx.ext.autodoc.AttributeDocumenter.priority

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        import sqlalchemy
        return isinstance(member, sqlalchemy.schema.Column)

    def add_content(self, more_content, no_docstring=False):
        # Revert back to default since the docstring *is* the correct thing to
        # display here.
        sphinx.ext.autodoc.ClassLevelDocumenter.add_content(
            self, more_content, no_docstring)
        self.add_line(u'   Type = Integer', '<autodoc>')

    def get_doc(self, encoding=None, ignore=1):
        content = self.env.config.autoclass_content
        docstrings = []
        attrdocstring = self.get_attr(self.object, 'doc', None)
        if attrdocstring:
            docstrings.append(attrdocstring)

        # for classes, what the "docstring" is can be controlled via a
        # config value; the default is only the class docstring
        if content in ('both', 'init'):
            initdocstring = self.get_attr(
                self.get_attr(self.object, '__init__', None), '__doc__')
            # for new-style classes, no __init__ means default __init__
            if initdocstring == object.__init__.__doc__:
                initdocstring = None
            if initdocstring:
                if content == 'init':
                    docstrings = [initdocstring]
                else:
                    docstrings.append(initdocstring)
        doc = []
        for docstring in docstrings:
            if not isinstance(docstring, unicode):
                docstring = force_decode(docstring, encoding)
            doc.append(prepare_docstring(docstring))
        return doc



class MapperDirective(sphinx.domains.python.PyClasslike):

    def get_index_text(self, modname, name_cls):
        if self.objtype == 'mapper':
            if not modname:
                return '%s (built-in mapper)' % name_cls[0]
            return '%s (%s mapper)' % (name_cls[0], modname)
        else:
            return ''


def setup(app):
    app.add_autodocumenter(ColumnAttributeDocumenter)
    app.add_autodocumenter(MapperDocumenter)
    domain = sphinx.domains.python.PythonDomain
    domain.object_types['mapper'] = sphinx.domains.python.ObjType(
        l_('mapper'), 'mapper', 'obj')
    domain.directives['mapper'] = MapperDirective
    domain.roles['mapper'] = sphinx.domains.python.PyXRefRole()
