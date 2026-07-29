from ir.allocators import ModuleAllocator


def test_allocator_sequential():
    alloc = ModuleAllocator()
    assert alloc.allocate() == 1
    assert alloc.allocate() == 2
    assert alloc.allocate() == 3


def test_allocator_reset():
    alloc = ModuleAllocator()
    assert alloc.allocate() == 1
    assert alloc.allocate() == 2
    alloc.reset()
    assert alloc.allocate() == 1
    assert alloc.allocate() == 2


def test_allocator_current():
    alloc = ModuleAllocator()
    assert alloc.current() == 0
    alloc.allocate()
    assert alloc.current() == 1
    alloc.allocate()
    alloc.allocate()
    assert alloc.current() == 3


def test_allocator_deterministic():
    alloc1 = ModuleAllocator()
    alloc2 = ModuleAllocator()

    seq1 = [alloc1.allocate() for _ in range(100)]
    seq2 = [alloc2.allocate() for _ in range(100)]

    assert seq1 == seq2
    assert alloc1.current() == alloc2.current()


def test_allocator_reset_deterministic():
    alloc1 = ModuleAllocator()
    alloc2 = ModuleAllocator()

    alloc1.allocate()
    alloc1.allocate()
    alloc1.reset()

    alloc2.allocate()
    alloc2.allocate()
    alloc2.reset()

    assert alloc1.allocate() == alloc2.allocate()
    assert alloc1.current() == alloc2.current()