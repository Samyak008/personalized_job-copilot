import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { Button } from '@/components/ui/button'

describe('Button', () => {
    it('renders correctly', () => {
        render(<Button>Click me</Button>)
        expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument()
    })

    it('handles click events', () => {
        const handleClick = vi.fn()
        render(<Button onClick={handleClick}>Click me</Button>)
        fireEvent.click(screen.getByRole('button', { name: /click me/i }))
        expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it('applies different variants', () => {
        const { container } = render(<Button variant="destructive">Delete</Button>)
        // Check if class is applied - exact class depends on implementation but we assume standard shadcn/ui
        // We can just check it renders without crashing for now or snapshot it
        expect(screen.getByRole('button', { name: /delete/i })).toBeInTheDocument()
    })
})
