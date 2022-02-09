from lunr import lunr

class OptionsState:

    label = "Please, choose an option:"
    invalid = "I could not understand this option. Please, try again."

    def __init__(self, comm, options=None):
        self.options = options or []
        self.matches = {}
        for key, label, function in self.options:
            pkey, plabel = self.preprocess(key), self.preprocess(label)
            self.matches[pkey] = function
            self.matches[plabel] = function
            self.matches[f"{pkey}. {plabel}"] = function
        self.initial(comm)
    
    def initial(self, comm):
        comm.reply(self.label)
        comm.reply([
            {'key': item[0], 'label': item[1]} for item in self.options
        ], "options")

    def preprocess(self, text):
        return str(text).strip().lower()

    def process_message(self, comm, text):
        newtext = self.preprocess(text)
        if newtext in self.matches:
            function = self.matches[newtext]
            return function(comm)
        comm.reply(self.invalid)
        return self


def build_document_list(tree):
    docmap = {}
    documents = []

    cid = 1
    visit = [("", tree)]
    while visit:
        current = visit.pop()
        newpath = current[0] + " " + current[1].name
        document = {
            'id': cid,
            'name': current[1].name,
            'path': newpath,
            'node': current[1]
        }
        documents.append(document)
        docmap[str(cid)] = document
        cid += 1
        for child in current[1].children:
            child.parent = current[1]
            visit.append((newpath, child))
    return docmap, documents


class SubjectState:

    def __init__(self, tree):
        self.docmap, documents = build_document_list(tree)
        self.idx = lunr(ref='id', fields=('name', 'path'), documents=documents)

    def process_message(self, comm, text):
        matches = self.idx.search(text)
        if not matches:
            comm.reply("I could not find this subject. Please, try a different query")
            return self
        return SubjectChoiceState(matches, comm, self)


class SubjectChoiceState(OptionsState):

    def __init__(self, matches, comm, subjectstate):
        self.subjectstate = subjectstate
        self.label = f"I found {len(matches)} subjects. Which one of these best describe your query?"
        options = []
        for i, match in enumerate(matches):
            label = subjectstate.docmap[match['ref']]['name']
            options.append((str(i + 1), label, self.load_subject_info(match, subjectstate)))
        options.append(('0', '(Go back to subject search)', self.load_subjectstate))
        super().__init__(comm, options)

    def load_subject_info(self, match, subjectstate):
        def load_info(comm):
            return SubjectInfoState(comm, subjectstate.docmap[match['ref']]['node'], subjectstate, self)
        return load_info

    def load_subjectstate(self, comm):
        return self.subjectstate


class SubjectInfoState(OptionsState):
    def __init__(self, comm, node, subjectstate, previousstate):
        self.label = f"What do you want to know about {node.name}?"
        self.node = node
        self.subjectstate = subjectstate
        self.previousstate = previousstate
        options = []
        cid = 1
        self.order = {}
        for key in self.node.attr:
            options.append((str(cid), key.replace("_", " ").capitalize(), self.attr(key)))
            cid += 1
        if self.node.parent is not None:
            options.append((str(cid), f"{self.node.parent.name} (parent)", self.subject(self.node.parent)))
            cid += 1
        for child in self.node.children:
            options.append((str(cid), f"{child.name} (child)", self.subject(child)))
            cid += 1
        options.append((str(cid), '(Back)', self.back))
        options.append(("0", '(Go back to subject search)', self.backsubject))
        super().__init__(comm, options)

    def attr(self, attr):
        def attr_display(comm):
            value = self.node.attr[attr]
            if isinstance(value, type):
                return value(comm, self, self.subjectstate)
            else:
                comm.reply(value)
                self.initial(comm)
                return self
        return attr_display

    def subject(self, child):
        def child_display(comm):
            return SubjectInfoState(comm, child, self.subjectstate, self)
        return child_display

    def back(self, comm):
        self.previousstate.initial(comm)
        return self.previousstate

    def backsubject(self, comm):
        return self.subjectstate


class DummyState:

    def process_message(self, comm, text):
        comm.reply(text + ", ditto")        
        return self
    
