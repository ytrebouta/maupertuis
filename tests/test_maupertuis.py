import random

from maupertuis import Maupertuis
from maupertuis.maupertuis import resolve, ANSI_CLEAR


# ------------------------------------------------------------------
# Level 1: one container, one pane
# ------------------------------------------------------------------

def test_single_pane_rows():

	layout = {'rows': [('a', -1)]}
	assert resolve(layout, 0, 0, 80, 24) == {'a': (0, 0, 80, 24)}

def test_single_pane_cols():

	layout = {'cols': [('a', -1)]}
	assert resolve(layout, 0, 0, 80, 24) == {'a': (0, 0, 80, 24)}


# ------------------------------------------------------------------
# Level 2: fixed sizes and one remaining pane
# ------------------------------------------------------------------

def test_fixed_exact_fit_rows():

	layout = {'rows': [('a', 10), ('b', 14)]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'a':	(0, 0, 80, 10),
		'b':	(0, 10, 80, 14),
	}

def test_fixed_exact_fit_cols():

	layout = {'cols': [('a', 30), ('b', 50)]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'a':	(0, 0, 30, 24),
		'b':	(30, 0, 50, 24),
	}

def test_remaining_first():

	layout = {'rows': [('a', -1), ('b', 4)]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'a':	(0, 0, 80, 20),
		'b':	(0, 20, 80, 4),
	}

def test_remaining_middle():

	layout = {'rows': [('a', 2), ('b', -1), ('c', 3)]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'a':	(0, 0, 80, 2),
		'b':	(0, 2, 80, 19),
		'c':	(0, 21, 80, 3),
	}

def test_remaining_last_cols():

	layout = {'cols': [('a', 20), ('b', -1)]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'a':	(0, 0, 20, 24),
		'b':	(20, 0, 60, 24),
	}

def test_unowned_space():

	# fixed sizes don't fill the container, the rest belongs to no pane

	layout = {'rows': [('a', 5), ('b', 3)]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'a':	(0, 0, 80, 5),
		'b':	(0, 5, 80, 3),
	}

def test_offset_origin():

	layout = {'rows': [('a', 2), ('b', -1)]}
	assert resolve(layout, 10, 5, 40, 12) == {
		'a':	(10, 5, 40, 2),
		'b':	(10, 7, 40, 10),
	}


# ------------------------------------------------------------------
# Level 3: several remaining panes
# ------------------------------------------------------------------

def test_remaining_even_split():

	layout = {'rows': [('a', -1), ('b', -1), ('c', -1)]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'a':	(0, 0, 80, 8),
		'b':	(0, 8, 80, 8),
		'c':	(0, 16, 80, 8),
	}

def test_remaining_uneven_split():

	# 24 rows / 5 panes: 4 each, the 4 extra rows go to the first 4 panes

	layout = {'rows': [(f'p{i}', -1) for i in range(5)]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'p0':	(0, 0, 80, 5),
		'p1':	(0, 5, 80, 5),
		'p2':	(0, 10, 80, 5),
		'p3':	(0, 15, 80, 5),
		'p4':	(0, 20, 80, 4),
	}

def test_remaining_uneven_around_fixed():

	# 81 - 10 = 71 columns for 2 remaining panes: 36 + 35

	layout = {'cols': [('a', -1), ('b', 10), ('c', -1)]}
	assert resolve(layout, 0, 0, 81, 24) == {
		'a':	(0, 0, 36, 24),
		'b':	(36, 0, 10, 24),
		'c':	(46, 0, 35, 24),
	}

def test_remaining_starved():

	# fixed sizes use all the space, the remaining pane gets 0 without error

	layout = {'rows': [('a', 24), ('b', -1)]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'a':	(0, 0, 80, 24),
		'b':	(0, 24, 80, 0),
	}


# ------------------------------------------------------------------
# Level 4: hidden panes
# ------------------------------------------------------------------

def test_hidden_pane_middle():

	layout = {'rows': [('a', -1), ('h', 0), ('b', 4)]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'a':	(0, 0, 80, 20),
		'h':	(0, 20, 80, 0),
		'b':	(0, 20, 80, 4),
	}

def test_hidden_panes_first_and_last():

	layout = {'cols': [('h1', 0), ('a', -1), ('h2', 0)]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'h1':	(0, 0, 0, 24),
		'a':	(0, 0, 80, 24),
		'h2':	(80, 0, 0, 24),
	}

def test_toggle_hidden_pane():

	# same layout, pane shown then hidden: the remaining pane absorbs its space

	shown	= {'rows': [('a', -1), ['debug', 5], ('b', 1)]}
	hidden	= {'rows': [('a', -1), ['debug', 0], ('b', 1)]}

	assert resolve(shown, 0, 0, 80, 24) == {
		'a':		(0, 0, 80, 18),
		'debug':	(0, 18, 80, 5),
		'b':		(0, 23, 80, 1),
	}
	assert resolve(hidden, 0, 0, 80, 24) == {
		'a':		(0, 0, 80, 23),
		'debug':	(0, 23, 80, 0),
		'b':		(0, 23, 80, 1),
	}


# ------------------------------------------------------------------
# Level 5: nesting
# ------------------------------------------------------------------

def test_cols_in_rows():

	layout = {'rows': [
		('stack',			-1),
		('input_top',		1),
		('input_field',		1),
		('input_bottom',	1),
		('debug_panel',		0),
		({'cols': [('status_bar', -1), ('status_ico', 4)]}, 2),
	]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'stack':		(0, 0, 80, 19),
		'input_top':	(0, 19, 80, 1),
		'input_field':	(0, 20, 80, 1),
		'input_bottom':	(0, 21, 80, 1),
		'debug_panel':	(0, 22, 80, 0),
		'status_bar':	(0, 22, 76, 2),
		'status_ico':	(76, 22, 4, 2),
	}

def test_rows_in_cols():

	layout = {'cols': [
		('side', 20),
		({'rows': [('top', 3), ('main', -1), ('bot', 1)]}, -1),
	]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'side':	(0, 0, 20, 24),
		'top':	(20, 0, 60, 3),
		'main':	(20, 3, 60, 20),
		'bot':	(20, 23, 60, 1),
	}

def test_fixed_size_container():

	layout = {'rows': [
		({'cols': [('l', -1), ('r', -1)]}, 5),
		('rest', -1),
	]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'l':	(0, 0, 40, 5),
		'r':	(40, 0, 40, 5),
		'rest':	(0, 5, 80, 19),
	}

def test_three_levels():

	layout = {'cols': [
		('side', 20),
		({'rows': [
			('top', 3),
			({'cols': [('a', -1), ('b', -1), ('c', -1)]}, -1),
			('bot', 1),
		]}, -1),
	]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'side':	(0, 0, 20, 24),
		'top':	(20, 0, 60, 3),
		'a':	(20, 3, 20, 20),
		'b':	(40, 3, 20, 20),
		'c':	(60, 3, 20, 20),
		'bot':	(20, 23, 60, 1),
	}


# ------------------------------------------------------------------
# Level 6: hidden and collapsed containers
# ------------------------------------------------------------------

def test_hidden_rows_in_rows():

	# children have fixed sizes, but the hidden container collapses without error

	layout = {'rows': [
		('stack', -1),
		({'rows': [('t', 1), ('b', 3)]}, 0),
		('s', 1),
	]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'stack':	(0, 0, 80, 23),
		't':		(0, 23, 80, 0),
		'b':		(0, 23, 80, 0),
		's':		(0, 23, 80, 1),
	}

def test_hidden_cols_in_cols():

	layout = {'cols': [
		('a', -1),
		({'cols': [('x', 10), ('y', -1)]}, 0),
	]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'a':	(0, 0, 80, 24),
		'x':	(80, 0, 0, 24),
		'y':	(80, 0, 0, 24),
	}

def test_hidden_cols_in_rows():

	# hidden along the other axis: height is 0, widths are still divided

	layout = {'rows': [
		('a', -1),
		({'cols': [('x', 10), ('y', -1)]}, 0),
	]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'a':	(0, 0, 80, 24),
		'x':	(0, 24, 10, 0),
		'y':	(10, 24, 70, 0),
	}

def test_hidden_deep_subtree():

	layout = {'rows': [
		('a', -1),
		({'rows': [
			('b', 2),
			({'cols': [('c', 5), ('d', -1)]}, 3),
		]}, 0),
	]}
	result = resolve(layout, 0, 0, 80, 24)

	assert result['a'] == (0, 0, 80, 24)
	for name in ('b', 'c', 'd'):
		_, _, w, h = result[name]
		assert w * h == 0, name

def test_squeezed_container_collapses():

	# a remaining container left with no space collapses instead of raising

	layout = {'rows': [
		('a', 24),
		({'rows': [('b', 1), ('c', 2)]}, -1),
	]}
	assert resolve(layout, 0, 0, 80, 24) == {
		'a':	(0, 0, 80, 24),
		'b':	(0, 24, 80, 0),
		'c':	(0, 24, 80, 0),
	}

def test_zero_height_terminal():

	layout = {'rows': [('a', -1), ('b', 3)]}
	assert resolve(layout, 0, 0, 80, 0) == {
		'a':	(0, 0, 80, 0),
		'b':	(0, 0, 80, 0),
	}


# ------------------------------------------------------------------
# Level 7: overflow errors
# ------------------------------------------------------------------

def raises_overflow(layout, width, height):

	try:
		resolve(layout, 0, 0, width, height)
	except ValueError:
		return True
	return False

def test_overflow_top_level():

	assert raises_overflow({'rows': [('a', 20), ('b', 10)]}, 80, 24)

def test_overflow_by_one():

	assert not	raises_overflow({'rows': [('a', 12), ('b', 12)]}, 80, 24)
	assert		raises_overflow({'rows': [('a', 12), ('b', 13)]}, 80, 24)

def test_overflow_nested():

	layout = {'rows': [
		({'cols': [('x', 50), ('y', 40)]}, 2),
		('r', -1),
	]}
	assert raises_overflow(layout, 80, 24)

def test_overflow_after_resize():

	layout = {'rows': [('main', -1), ('a', 3), ('b', 3)]}

	assert not	raises_overflow(layout, 80, 24)
	assert not	raises_overflow(layout, 80, 6)
	assert		raises_overflow(layout, 80, 5)


# ------------------------------------------------------------------
# Level 8: resize
# ------------------------------------------------------------------

def test_resize_sequence():

	layout = {'rows': [('stack', -1), ('input', 1), ('status', 2)]}

	for height in (3, 4, 10, 24, 60):
		result = resolve(layout, 0, 0, 100, height)
		assert result['stack']	== (0, 0, 100, height - 3)
		assert result['input']	== (0, height - 3, 100, 1)
		assert result['status']	== (0, height - 2, 100, 2)


# ------------------------------------------------------------------
# Level 9: random layouts, checked against an independent recursive
#          version and against geometric invariants
# ------------------------------------------------------------------

def oracle(node, x0, y0, width, height):

	# the earlier recursive resolve(), used as a reference

	if isinstance(node, str):
		return {node: (x0, y0, width, height)}

	direction	= 'rows' if 'rows' in node else 'cols'
	children	= node[direction]
	total_span	= height if direction == 'rows' else width
	collapsed	= total_span == 0

	fixed_total	= sum(size for _, size in children if size > 0)
	n_remaining	= sum(1 for _, size in children if size == -1)

	if fixed_total > total_span and not collapsed:
		raise ValueError('overflow')

	base_share, extra	= divmod(total_span - fixed_total, n_remaining) if n_remaining else (0, 0)
	pos					= 0
	rem_i				= 0
	result				= {}

	for child_node, size in children:

		if collapsed:
			span	= 0
		elif size == -1:
			span	= base_share + (1 if rem_i < extra else 0)
			rem_i	+= 1
		else:
			span	= size

		if direction == 'rows':
			result.update(oracle(child_node, x0, y0 + pos, width, span))
		else:
			result.update(oracle(child_node, x0 + pos, y0, span, height))

		pos += span

	return result

def random_layout(rng, counter, depth=0):

	# every container gets at least one remaining child, so panes must cover the screen

	sizes		= [-1] + [rng.choice([-1, -1, 0, 1, 2, 3, 5]) for _ in range(rng.randint(0, 4))]
	rng.shuffle(sizes)
	children	= []

	for size in sizes:
		if depth < 3 and rng.random() < 0.3:
			child = random_layout(rng, counter, depth + 1)
		else:
			counter[0]	+= 1
			child		= f'p{counter[0]}'
		children.append((child, size))

	return {rng.choice(['rows', 'cols']): children}

def leaf_names(node):

	if isinstance(node, str):
		return [node]

	children = node['rows'] if 'rows' in node else node['cols']
	return [name for child, _ in children for name in leaf_names(child)]

def overlap(a, b):

	ax, ay, aw, ah = a
	bx, by, bw, bh = b
	return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah

def test_random_layouts():

	rng			= random.Random(1234)
	checked		= 0
	overflows	= 0

	for _ in range(3000):

		layout			= random_layout(rng, [0])
		width, height	= rng.randint(0, 120), rng.randint(0, 50)

		try:
			expected = oracle(layout, 0, 0, width, height)
		except ValueError:
			assert raises_overflow(layout, width, height)
			overflows += 1
			continue

		result = resolve(layout, 0, 0, width, height)

		# same rectangles as the reference

		assert result == expected

		# every pane present

		assert sorted(result) == sorted(leaf_names(layout))

		# every rect inside the screen

		for x, y, w, h in result.values():
			assert w >= 0 and h >= 0
			assert x >= 0 and y >= 0 and x + w <= width and y + h <= height

		# visible panes never overlap

		visible = [r for r in result.values() if r[2] * r[3] > 0]
		for i in range(len(visible)):
			for j in range(i + 1, len(visible)):
				assert not overlap(visible[i], visible[j])

		# panes cover the whole screen

		assert sum(w * h for _, _, w, h in result.values()) == width * height

		checked += 1

	assert checked > 1000 and overflows > 0
	print(f"{checked} layouts checked, {overflows} overflows")



# ------------------------------------------------------------------
# Level 10: sanity checks in resolve()
# ------------------------------------------------------------------

def raises(exc, fn, *args):

	try:
		fn(*args)
	except exc:
		return True
	return False

def test_duplicate_name_same_container():

	assert raises(ValueError, resolve, {'rows': [('a', 1), ('a', -1)]}, 0, 0, 80, 24)

def test_duplicate_name_across_branches():

	layout = {'rows': [
		({'cols': [('a', -1)]}, 1),
		({'cols': [('a', -1)]}, -1),
	]}
	assert raises(ValueError, resolve, layout, 0, 0, 80, 24)

def test_duplicate_name_in_hidden_subtree():

	layout = {'rows': [
		('a', -1),
		({'rows': [('a', 1)]}, 0),
	]}
	assert raises(ValueError, resolve, layout, 0, 0, 80, 24)

def test_invalid_sizes():

	for size in (-5, -2, 1.5, True, '3', None):
		assert raises(ValueError, resolve, {'rows': [('a', size)]}, 0, 0, 80, 24), size

def test_valid_sizes_accepted():

	for size in (-1, 0, 1, 24):
		resolve({'rows': [('a', size)]}, 0, 0, 80, 24)

def test_container_with_both_keys():

	layout = {'rows': [('a', -1)], 'cols': [('b', -1)]}
	assert raises(ValueError, resolve, layout, 0, 0, 80, 24)

def test_container_with_no_key():

	assert raises(ValueError, resolve, {'row': [('a', -1)]}, 0, 0, 80, 24)

def test_container_named_by_id_only():

	assert raises(ValueError, resolve, {'id': 'x'}, 0, 0, 80, 24)

def test_top_level_not_a_container():

	assert raises(ValueError, resolve, 'main', 0, 0, 80, 24)

def test_child_neither_pane_nor_container():

	assert raises(ValueError, resolve, {'rows': [(42, -1)]}, 0, 0, 80, 24)

def test_checks_run_in_collapsed_containers():

	# a hidden subtree is still checked

	layout = {'rows': [('a', -1), ({'rows': [('b', -7)]}, 0)]}
	assert raises(ValueError, resolve, layout, 0, 0, 80, 24)


# ------------------------------------------------------------------
# Level 11: the Maupertuis class
# ------------------------------------------------------------------

CALC = {'rows': [
	('stack',			-1),
	('input_top',		1),
	('input_field',		1),
	('input_bottom',	1),
	('debug_panel',		0),
	({'cols': [('status_bar', -1), ('status_ico', 4)]}, 2),
]}

CALC_DEBUG = {'rows': [
	('stack',			-1),
	('input_top',		1),
	('input_field',		1),
	('input_bottom',	1),
	('debug_panel',		5),
	({'cols': [('status_bar', -1), ('status_ico', 4)]}, 2),
]}

def recorder(name):

	return lambda x0, y0, w, h: f"[{name} {x0},{y0},{w},{h}]"

def calc_fns():

	return {name: recorder(name) for name in resolve(CALC, 0, 0, 80, 24)}

def test_constructor_builds():

	mp = Maupertuis(CALC, calc_fns(), 80, 24)
	assert mp.panes == resolve(CALC, 0, 0, 80, 24)
	assert mp.draw().startswith(ANSI_CLEAR)

def test_constructor_missing_draw_fn():

	fns = calc_fns()
	del fns['stack']
	assert raises(ValueError, Maupertuis, CALC, fns, 80, 24)

def test_constructor_unused_draw_fn():

	fns = calc_fns()
	fns['ghost'] = recorder('ghost')
	assert raises(ValueError, Maupertuis, CALC, fns, 80, 24)

def test_constructor_invalid_layout():

	fns = {'a': recorder('a')}
	assert raises(ValueError, Maupertuis, {'rows': [('a', -3)]}, fns, 80, 24)

def test_constructor_terminal_too_small():

	assert raises(ValueError, Maupertuis, CALC, calc_fns(), 80, 4)

def test_first_draw_is_full():

	mp = Maupertuis(CALC, calc_fns(), 80, 24)

	# clear first, then every visible pane in layout order; debug_panel is hidden

	assert mp.draw() == (ANSI_CLEAR
		+ '[stack 0,0,80,19]'
		+ '[input_top 0,19,80,1]'
		+ '[input_field 0,20,80,1]'
		+ '[input_bottom 0,21,80,1]'
		+ '[status_bar 0,22,76,2]'
		+ '[status_ico 76,22,4,2]')

def test_nothing_dirty_draws_nothing():

	mp = Maupertuis(CALC, calc_fns(), 80, 24)
	mp.draw()
	assert mp.draw() == ''

def test_mark_draws_only_marked():

	mp = Maupertuis(CALC, calc_fns(), 80, 24)
	mp.draw()

	mp.mark('input_field')
	assert mp.draw() == '[input_field 0,20,80,1]'
	assert mp.draw() == ''

def test_mark_several():

	mp = Maupertuis(CALC, calc_fns(), 80, 24)
	mp.draw()

	mp.mark('stack')
	mp.mark('status_ico')
	mp.mark('stack')
	out = mp.draw()

	# a set has no order: check the parts, each drawn once

	assert sorted(out.replace('][', ']|[').split('|')) == ['[stack 0,0,80,19]', '[status_ico 76,22,4,2]']

def test_mark_hidden_pane_draws_nothing():

	mp = Maupertuis(CALC, calc_fns(), 80, 24)
	mp.draw()

	mp.mark('debug_panel')
	assert mp.draw() == ''
	assert mp.dirty == set()

def test_mark_unknown_pane():

	mp = Maupertuis(CALC, calc_fns(), 80, 24)
	assert raises(KeyError, mp.mark, 'stak')

def test_build_redraws_like_first_frame():

	mp = Maupertuis(CALC, calc_fns(), 80, 24)
	first = mp.draw()

	mp.mark('stack')
	mp.build()
	assert mp.draw() == first
	assert mp.draw() == ''

def test_build_forces_full_redraw_and_empties_dirty():

	mp = Maupertuis(CALC, calc_fns(), 80, 24)
	mp.draw()

	mp.mark('stack')
	mp.build(100, 30)
	assert mp.dirty == set()
	out = mp.draw()
	assert out.startswith(ANSI_CLEAR)
	assert '[stack 0,0,100,25]' in out

def test_build_without_size_reuses_last():

	mp = Maupertuis(CALC, calc_fns(), 100, 30)
	mp.build()
	assert mp.panes['stack'] == (0, 0, 100, 25)

def test_build_one_dimension():

	mp = Maupertuis(CALC, calc_fns(), 100, 30)
	mp.build(height=10)
	assert mp.panes['stack'] == (0, 0, 100, 5)

def test_switch_layout():

	mp = Maupertuis(CALC, calc_fns(), 80, 24)
	mp.draw()

	mp.layout = CALC_DEBUG
	mp.build()
	assert mp.panes['stack']		== (0, 0, 80, 14)
	assert mp.panes['debug_panel']	== (0, 17, 80, 5)
	assert '[debug_panel 0,17,80,5]' in mp.draw()

def test_switch_layout_with_mismatched_names():

	mp = Maupertuis(CALC, calc_fns(), 80, 24)
	before = dict(mp.panes)

	mp.layout = {'rows': [('stack', -1), ('new_pane', 1)]}
	assert raises(ValueError, mp.build)
	assert mp.panes == before

def test_too_small_keeps_previous_panes():

	mp = Maupertuis(CALC, calc_fns(), 80, 24)
	before = dict(mp.panes)

	assert raises(ValueError, mp.build, 80, 4)
	assert mp.panes == before

def test_custom_clear_str():

	mp = Maupertuis(CALC, calc_fns(), 80, 24, clear_str='<CLEAR>')
	assert mp.draw().startswith('<CLEAR>[stack')

def test_draw_fn_gets_rect():

	seen = {}

	def spy(x0, y0, w, h):
		seen['rect'] = (x0, y0, w, h)
		return ''

	fns = calc_fns()
	fns['status_ico'] = spy
	mp = Maupertuis(CALC, fns, 80, 24)
	mp.draw()
	assert seen['rect'] == (76, 22, 4, 2)


# ------------------------------------------------------------------

if __name__ == '__main__':

	tests	= [(name, fn) for name, fn in globals().items() if name.startswith('test_')]
	failed	= 0

	for name, fn in tests:
		try:
			fn()
			print(f"PASS  {name}")
		except AssertionError as e:
			failed += 1
			print(f"FAIL  {name}  {e}")
		except Exception as e:
			failed += 1
			print(f"ERROR {name}  {type(e).__name__}: {e}")

	print(f"\n{len(tests) - failed}/{len(tests)} passed")
