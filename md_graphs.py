#!/usr/bin/python3
'''
title : Graphviz DOT to SVG
author : qkzk
date : 2021/04/22

read a markdown make it a SVG
'''
from subprocess import call
import argparse



DEFAULT_FILE_NAME = "_index.md"

def _argument_reader() -> argparse.Namespace:
    """
    parse the command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Copy a markdown, replacing graph codeblock by a link to generated svg"
    )
    parser.add_argument("intput")
    parser.add_argument(
        "-o", "--output", help="output", action="store", default=DEFAULT_FILE_NAME
    )

    args = parser.parse_args()

    return args

def _parse_args(args: argparse.Namespace) -> tuple:
    '''
    return the input and output filenames
    '''
    return args.intput, args.output


def _read_text(filename: str) -> list[str]:
    '''
    extract the text content of the file
    '''
    with open(filename, encoding="utf-8") as markdown_file:
        file_content = markdown_file.readlines()
    return file_content

def _name_graph_from_index(index: int) -> str:
    '''
    return the name of a graph from it's index
    '''
    return f"graph_{index:0>3}.svg"


class MdReader:

    '''
    reader of markdown files
    '''

    GRAPH_OPENER = "```graph"
    GRAPH_CLOSER = "```"

    def __init__(self, file_content):
        self.file_content = file_content
        self.graphs_lines: list[tuple[int, int, int]] = []


    def _search_graphs(self):
        '''
        search all ```graph
        '''
        for line_nr, line in enumerate(self.file_content):
            if line.lstrip().lower().startswith(self.GRAPH_OPENER):
                line_start = line_nr
                size = self._search_graph_closer(line_nr)
                indent = self._mesure_line_indentation(line)
                self.graphs_lines.append((line_start, size, indent))

    def _search_graph_closer(self, line_start: int) -> int:
        '''
        return the first closing code block line
        '''
        # TODO : should be an easier way
        size = 0
        for line in self.file_content[line_start + 1:]:
            size += 1
            if line.lstrip().lower().startswith(self.GRAPH_CLOSER):
                return size
        raise ValueError("Graphviz error : The closing block can't be found")

    @staticmethod
    def _mesure_line_indentation(line_content: str) -> int:
        '''
        count the nbr of spaces before the starting of the line
        '''
        return len(line_content) - len(line_content.lstrip(" "))

    @classmethod
    def extract_graphs_lines(cls, file_content) -> list[tuple[int, int, int]]:
        '''
        return a list of indexes of graphs
        '''
        obj = cls(file_content)
        obj._search_graphs()
        return obj.graphs_lines

class Parser:

    '''
    Parser of markdown files
    '''

    def __init__(self, file_content, positions: list[tuple[int, int, int]]):
        self.file_content = file_content
        self.positions = positions

    def _extract_text(self, line_start: int, size: int, _: int):
        '''
        extract the text from those lines
        '''
        return "".join([line.lstrip()
            for line in self.file_content[line_start + 1: line_start + size]])

    @classmethod
    def extract_graphs(
        cls,
        markdown_file,
        positions: list[tuple[int, int, int]]
    ) -> list[str]:
        '''
        return the graphs descriptions from the content
        '''
        parser = cls(markdown_file, positions)
        return [parser._extract_text(*position)
                for position in positions]


class DotObject:
    '''
    Represent a dot object
    '''

    def __init__(self, description: str):
        self.description = description


    def __to_something(self, filename, something: str):
        """ 
        Create the image corresponding to the representation of the
        specified Graph in a file.
        The Graph is converted in DOT format and the command dot is called
        in order to generate the image.
        """

        tmp_file = filename + ".tmp"
        with open(tmp_file, "w") as file_content:
            file_content.write(self.description)

        call((f"dot -T{something} " + tmp_file + " -o " + filename).split(" "))
        call(("rm " + tmp_file).split(" "))

    def to_png(self, filename):
        '''
        Creates a PNG representation of the Graph using the dot command
        '''
        self.__to_something(filename, "png")


    def to_svg(self, filename):
        '''
        return the SVG description of the graph
        '''
        self.__to_something(filename, "svg")

class Replacer:

    '''
    Replace the graph by a link to SVG file
    '''

    def __init__(self, filename: str, file_content: list[str], positions: list[tuple[int, int, int]]):
        self.filename = filename
        self.file_content = file_content
        self.positions = positions
        self.graphs_indexes = {position[0]: index
                               for index, position in enumerate(positions)}

    @staticmethod
    def _create_link(index, indent: int) -> str:
        graph_name = _name_graph_from_index(index)
        return " " * indent + f"![{graph_name}]({graph_name})\n\n"

    def _write_lines(self, new_file):
        with open(new_file, "w") as dest_file:
            for line_nr, line in enumerate(self.file_content):
                if not self._is_a_graph_line(line_nr):
                    dest_file.write(line)

                elif self._line_is_a_start_graph(line_nr):
                    self._write_graph_link(line_nr, dest_file)

    def _write_graph_link(self, line_nr: int, dest_file):
        '''
        Write the link of the graph that was there in the original file
        '''
        index = self._get_graph_index_from_line_nr(line_nr)
        indent = self.positions[index][2]
        link = self._create_link(index, indent)
        dest_file.write(link)

    def _get_graph_index_from_line_nr(self, line_number: int) -> int:
        '''
        return the corresponding index of a graph from his line_nr
        '''
        return self.graphs_indexes[line_number]

    def _line_is_a_start_graph(self, line_number) -> bool:
        '''
        True iff the line is the beginning of a graph code block
        '''
        return self.graphs_indexes.get(line_number, None) is not None

    def _is_a_graph_line(self, line_number: int):
        '''
        True iff the line is between graph code blocks
        It checks every positions
        '''
        for start, size, _ in self.positions:
            if start <= line_number <= start + size:
                return True
        return False

    @classmethod
    def replace(
        cls,
        filename: str,
        file_content: list[str],
        positions: list[tuple[int, int, int]],
        new_file=str
    ):
        '''
        Creates a copy of the file (filename) whose lines are either copied if
        they're not between graph code blocks or replaced by a link to the
        said graph
        '''
        replacer = cls(filename, file_content, positions)
        replacer._write_lines(new_file=new_file)


def main():
    '''
    runs the module of a file
    '''
    intput_file, output_file = _parse_args(_argument_reader())
    markdown_file = _read_text(intput_file)
    positions = MdReader.extract_graphs_lines(markdown_file)
    graph_descriptions = Parser.extract_graphs(markdown_file, positions)
    for index, graph in enumerate(graph_descriptions):
        dot_object = DotObject(graph)
        # TODO i don't need PNG
        # dot_object.to_png(f"graph_{index:0>3}.png")
        dot_object.to_svg(_name_graph_from_index(index))
    Replacer.replace(intput_file, markdown_file, positions, output_file)

if __name__ == "__main__":
    main()
