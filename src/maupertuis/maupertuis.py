ANSI_CLEAR = '\x1b[2J\x1b[H'		# clear screen, cursor home


def resolve(layout, x0, y0, width, height):

	result	= {}
	todo	= [(layout, x0, y0, width, height)]	# containers still to process, with their rect

	while todo:

		node, x0, y0, width, height = todo.pop()

		# Sanity check

		if not isinstance(node, dict) or ('rows' in node) == ('cols' in node):
			raise ValueError(f"container must be a dict with either 'rows' or 'cols': {node!r}")

		direction	= 'rows' if 'rows' in node else 'cols'
		children	= node[direction]
		total_span	= height if direction == 'rows' else width
		collapsed	= total_span == 0
		fixed_total	= 0
		n_remaining	= 0

		for child_node, size in children:

			if type(size) is not int or size < -1:
				raise ValueError(f"invalid size {size!r} for {child_node!r}: use a positive int, 0 or -1")

			if size > 0:
				fixed_total += size

			elif size == -1:
				n_remaining += 1

		if fixed_total > total_span and not collapsed:
			raise ValueError(f"layout overflow: fixed sizes ({fixed_total}) exceed available space ({total_span})")

		leftover			= total_span - fixed_total
		base_share, extra	= divmod(leftover, n_remaining) if n_remaining else (0, 0)

		# Compute each child's rect: panes go to result, containers go back to todo

		pos		= 0

		for child_node, size in children:

			if collapsed:
				span	= 0

			elif size == -1:

				if extra:
					span	= base_share + 1
					extra	-= 1

				else:
					span	= base_share

			else:
				span	= size

			if direction == 'rows':
				rect = (x0, y0 + pos, width, span)

			else:
				rect = (x0 + pos, y0, span, height)

			if isinstance(child_node, str):
				if child_node in result:
					raise ValueError(f"duplicate pane id: {child_node!r}")

				result[child_node] = rect

			else:
				todo.append((child_node, *rect))

			pos += span

	return result


class Maupertuis:

	def __init__(self, layout, draw_fns, width, height, clear_str=ANSI_CLEAR):

		self.layout			= layout
		self.draw_fns		= draw_fns
		self.clear_str		= clear_str
		self.width			= width
		self.height			= height
		self.panes			= {}
		self.dirty			= set()
		self.full_redraw	= False

		self.build()

	def build(self, width=None, height=None):

		# If called without a term resize, keeps the old values.

		if width is not None:
			self.width = width

		if height is not None:
			self.height = height

		panes				= resolve(self.layout, 0, 0, self.width, self.height)
		self.chk_ids(panes)
		self.panes			= panes
		self.dirty.clear()
		self.full_redraw	= True

	def chk_ids(self, panes):

		draws_k	= self.draw_fns.keys()
		panes_k	= panes.keys()
		missing	= panes_k - draws_k
		unused	= draws_k - panes_k

		if missing or unused:
			raise ValueError(f"pane ids without draw function: {sorted(missing)}, draw functions without pane id: {sorted(unused)}")

	def mark(self, pane_id):

		if pane_id not in self.draw_fns:
			raise KeyError(f"unknown pane id: {pane_id!r}")

		self.dirty.add(pane_id)

	def draw(self):

		if self.full_redraw:
			pane_ids	= self.panes
			out			= [self.clear_str]

		else:
			pane_ids	= self.dirty
			out			= []

		for pane_id in pane_ids:
			x0, y0, w, h = self.panes[pane_id]

			if w == 0 or h == 0:
				continue

			out.append(self.draw_fns[pane_id](x0=x0, y0=y0, w=w, h=h))

		self.dirty.clear()
		self.full_redraw = False

		return ''.join(out)