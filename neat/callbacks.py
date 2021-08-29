from neat.genome import Genome
import os.path
import time
from collections import deque


class GenomeSaving():
    def __init__(self, population, top=1, override=True, dir='', filenames=[]):
        self.top = top if top > 0 else population
        self.override = override
        self.filepaths = [os.path.join(dir, filename) for filename in filenames] if len(filenames) == top else \
        [os.path.join(dir, f'genome-{idx}.{Genome.FILE_EXT}' if self.override else f'genome-{idx}') for idx in range(top)]


    def __call__(self, neat, generation, sort=False):
        if sort:
            neat.sort_genomes()
        
        if self.override:
            for idx in range(self.top):
                neat.genomes[idx].save(path=self.filepaths[idx])
            
            return

        for idx in range(self.top):
            neat.genomes[idx].save(path=self.filepaths[idx] + f'-gen-{generation}.{Genome.FILE_EXT}')


class GenerationTermination():
    def __init__(self, stop_at):
        self.stop_at = stop_at


    def __call__(self, neat, curr_generation):
        return curr_generation >= self.stop_at


class FitnessTermination():
    def __init__(self, termination_fitness, top=1):
        self.termination_fitness = termination_fitness
        self.top = top
    

    def __call__(self, neat, sorted=False):
        if sorted:
            for idx in range(self.top):
                if neat.genomes[idx].fitness < self.termination_fitness:
                    return False
        
            return True
        
        count = 0

        for genome in neat.genomes:
            if genome.fitness >= self.termination_fitness:
                count += 1

                if count == self.top:
                    return True
        
        return False


class TimeTermination():
    def __init__(self, hours, minutes=0, seconds=0):
        self.run_time = hours * 3600 + minutes * 60 + seconds

        self.start_time = time.perf_counter()


    def __call__(self):
        return (time.perf_counter() - self.start_time) >= self.run_time


class FileLogger():
    def __init__(self, filepath, population, top=1):
        self.filepath = filepath
        self.top = top if top is not None else population
        self.data = deque()

    
    def __call__(self, neat, generation, sort=False):
        if sort:
            neat.sort_genomes()
        
        self.data.append(f'Gen {generation},{",".join([genome.fitness for genome in neat.genomes])}\n')
        
        with open(self.filepath, 'w+') as file:
            file.writelines(self.data)