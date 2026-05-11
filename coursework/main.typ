#import "@preview/modern-g7-32:0.2.0": gost
#import "const.typ"

#show: gost.with(
  text-size: const.text-size,
  indent: const.indent,
  hide-title: true,
)

#set text(font: "Times New Roman")
#set block(
  above: auto,
  below: const.leading-one-and-a-half,
)
#set par(
  leading: const.leading-one-and-a-half,
  spacing: const.leading-one-and-a-half,
)

#show outline: set block(
  above: auto,
  below: const.leading-one-and-a-half,
)

#set heading(
  hanging-indent: -const.indent,
)
#show heading: set par(
  justify: true,
  leading: const.leading-one,
)
#show heading: set block(
  above: auto,
  below: const.leading-one-and-a-half,
)

#show list: it => {
  for child in it.children {
    let marker = "–"
    par[#marker#h(const.leading-one)#child.body]
  }
}
#show enum: it => {
  let current-num = 0
  for child in it.children {
    current-num = if child.number == auto {
      current-num + 1
    } else {
      child.number
    }
    let num = numbering("1)", current-num)
    par[#num#h(const.leading-one)#child.body]
  }
}

#show table: it => {
  set block(breakable: true)

  show table.cell: cell => {
    set align(if cell.y == 0 { center + horizon } else { left + top })
    cell
  }

  it
}
#set table(stroke: const.stroke)

#set figure.caption(separator: " – ")

#show figure: it => {
  show figure.caption: set text(size: const.text-size.default)
  set par(leading: const.leading-one)
  block(breakable: false, below: const.leading-one, { it })
}
#show figure.where(kind: table): it => {
  set text(size: const.text-size.small)
  set par(justify: false)
  block(breakable: false, below: const.leading-one, { it })
}
#show figure.where(kind: raw): it => {
  block(breakable: false, below: const.leading-one, {
    align(left, it.caption)
    set text(size: const.text-size.small)
    table(
      columns: (1fr,),
      stroke: const.stroke,
      align: left,
      it.body,
    )
  })
}

#include "content/00-title.typ"

#include "content/01-abstract.typ"

#outline(indent: const.outline-indent)

#include "content/02-terms.typ"

#include "content/03-intro.typ"

#include "content/04-body.typ"

#include "content/05-conclusion.typ"

#bibliography("refs.yaml")

